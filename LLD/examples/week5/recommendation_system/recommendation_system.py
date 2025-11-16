"""
Recommendation System - Low Level Design Implementation

This module implements a comprehensive recommendation system with:
- Collaborative Filtering (User-Based)
- Content-Based Filtering
- Hybrid Recommendation Approach
- Strategy, Factory, and Observer Design Patterns

Author: LLD Course
Week: 5 - Advanced System Designs
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional
from enum import Enum
import math
from collections import defaultdict


# ============================================================================
# ENUMS AND VALUE OBJECTS
# ============================================================================

class RecommendationEventType(Enum):
    """Types of recommendation events"""
    RATING_ADDED = "rating_added"
    RATING_UPDATED = "rating_updated"
    RECOMMENDATIONS_GENERATED = "recommendations_generated"
    STRATEGY_CHANGED = "strategy_changed"


# ============================================================================
# CORE ENTITIES
# ============================================================================

class User:
    """Represents a user in the recommendation system"""

    def __init__(self, user_id: str, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.preferences: Set[str] = set()
        self.demographics: Dict[str, str] = {}
        self._ratings: Dict[str, 'Rating'] = {}  # item_id -> Rating

    def add_preference(self, preference: str) -> None:
        """Add a user preference/interest"""
        self.preferences.add(preference)

    def add_rating(self, rating: 'Rating') -> None:
        """Add or update a rating"""
        self._ratings[rating.item_id] = rating

    def get_ratings(self) -> Dict[str, 'Rating']:
        """Get all user ratings"""
        return self._ratings.copy()

    def get_rating(self, item_id: str) -> Optional['Rating']:
        """Get rating for specific item"""
        return self._ratings.get(item_id)

    def get_average_rating(self) -> float:
        """Calculate average rating given by user"""
        if not self._ratings:
            return 0.0
        return sum(r.rating for r in self._ratings.values()) / len(self._ratings)

    def get_profile(self) -> Dict:
        """Get user profile information"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'preferences': self.preferences,
            'demographics': self.demographics,
            'rating_count': len(self._ratings),
            'average_rating': self.get_average_rating()
        }

    def __repr__(self) -> str:
        return f"User(id={self.user_id}, name={self.name}, ratings={len(self._ratings)})"


class Item:
    """Represents an item that can be recommended"""

    def __init__(self, item_id: str, title: str, category: str):
        self.item_id = item_id
        self.title = title
        self.category = category
        self.tags: Set[str] = set()
        self.features: Dict[str, float] = {}  # Feature name -> value
        self.metadata: Dict[str, str] = {}
        self._ratings: List['Rating'] = []

    def add_tag(self, tag: str) -> None:
        """Add a tag to the item"""
        self.tags.add(tag)

    def add_feature(self, feature_name: str, value: float) -> None:
        """Add a feature with its value"""
        self.features[feature_name] = value

    def add_rating(self, rating: 'Rating') -> None:
        """Record a rating for this item"""
        self._ratings.append(rating)

    def get_features(self) -> Dict[str, float]:
        """Get all item features"""
        return self.features.copy()

    def get_feature_vector(self) -> List[float]:
        """Get feature values as a vector (ordered by feature name)"""
        sorted_features = sorted(self.features.items())
        return [value for _, value in sorted_features]

    def get_average_rating(self) -> float:
        """Calculate average rating for this item"""
        if not self._ratings:
            return 0.0
        return sum(r.rating for r in self._ratings) / len(self._ratings)

    def get_rating_count(self) -> int:
        """Get number of ratings"""
        return len(self._ratings)

    def __repr__(self) -> str:
        return f"Item(id={self.item_id}, title={self.title}, category={self.category})"


class Rating:
    """Represents a user's rating of an item"""

    def __init__(self, user_id: str, item_id: str, rating: float):
        if not 1.0 <= rating <= 5.0:
            raise ValueError("Rating must be between 1.0 and 5.0")

        self.user_id = user_id
        self.item_id = item_id
        self.rating = rating
        self.timestamp = datetime.now()

    def update_rating(self, new_rating: float) -> None:
        """Update the rating value"""
        if not 1.0 <= new_rating <= 5.0:
            raise ValueError("Rating must be between 1.0 and 5.0")

        self.rating = new_rating
        self.timestamp = datetime.now()

    def get_rating(self) -> float:
        """Get the rating value"""
        return self.rating

    def __repr__(self) -> str:
        return f"Rating(user={self.user_id}, item={self.item_id}, rating={self.rating})"


# ============================================================================
# SIMILARITY METRICS (Strategy Pattern for Similarity Calculation)
# ============================================================================

class SimilarityMetric(ABC):
    """Abstract base class for similarity metrics"""

    @abstractmethod
    def calculate(self, vector_a: List[float], vector_b: List[float]) -> float:
        """Calculate similarity between two vectors"""
        pass


class CosineSimilarity(SimilarityMetric):
    """Cosine similarity metric"""

    def calculate(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Calculate cosine similarity: cos(θ) = (A·B) / (||A|| ||B||)
        Returns value between -1 and 1 (1 = identical, 0 = orthogonal, -1 = opposite)
        """
        if len(vector_a) != len(vector_b):
            raise ValueError("Vectors must have same length")

        if not vector_a or not vector_b:
            return 0.0

        # Dot product
        dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

        # Magnitudes
        magnitude_a = math.sqrt(sum(a * a for a in vector_a))
        magnitude_b = math.sqrt(sum(b * b for b in vector_b))

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)


class PearsonCorrelation(SimilarityMetric):
    """Pearson correlation coefficient"""

    def calculate(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Calculate Pearson correlation coefficient
        Returns value between -1 and 1
        """
        if len(vector_a) != len(vector_b):
            raise ValueError("Vectors must have same length")

        if not vector_a or not vector_b:
            return 0.0

        n = len(vector_a)
        if n == 0:
            return 0.0

        # Calculate means
        mean_a = sum(vector_a) / n
        mean_b = sum(vector_b) / n

        # Calculate correlation
        numerator = sum((a - mean_a) * (b - mean_b) for a, b in zip(vector_a, vector_b))

        variance_a = sum((a - mean_a) ** 2 for a in vector_a)
        variance_b = sum((b - mean_b) ** 2 for b in vector_b)

        denominator = math.sqrt(variance_a * variance_b)

        if denominator == 0:
            return 0.0

        return numerator / denominator


class EuclideanDistance(SimilarityMetric):
    """Euclidean distance (converted to similarity)"""

    def calculate(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Calculate Euclidean distance and convert to similarity
        Returns value between 0 and 1 (1 = identical)
        """
        if len(vector_a) != len(vector_b):
            raise ValueError("Vectors must have same length")

        if not vector_a or not vector_b:
            return 0.0

        # Calculate Euclidean distance
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(vector_a, vector_b)))

        # Convert distance to similarity (0 to 1)
        return 1.0 / (1.0 + distance)


# ============================================================================
# RECOMMENDATION STRATEGIES (Strategy Pattern)
# ============================================================================

class RecommendationStrategy(ABC):
    """Abstract base class for recommendation strategies"""

    def __init__(self, users: Dict[str, User], items: Dict[str, Item]):
        self.users = users
        self.items = items

    @abstractmethod
    def recommend(self, user: User, n: int = 10,
                 exclude_rated: bool = True) -> List[Tuple[Item, float]]:
        """
        Generate top N recommendations for a user
        Returns list of (Item, score) tuples sorted by score
        """
        pass

    @abstractmethod
    def explain_recommendation(self, user: User, item: Item) -> str:
        """Provide explanation for why item was recommended"""
        pass


class CollaborativeFilteringStrategy(RecommendationStrategy):
    """User-based collaborative filtering recommendation strategy"""

    def __init__(self, users: Dict[str, User], items: Dict[str, Item],
                 similarity_metric: SimilarityMetric = None,
                 min_common_items: int = 2):
        super().__init__(users, items)
        self.similarity_metric = similarity_metric or CosineSimilarity()
        self.min_common_items = min_common_items
        self._similarity_cache: Dict[Tuple[str, str], float] = {}

    def _get_user_vector(self, user: User, common_items: Set[str]) -> List[float]:
        """Get user rating vector for common items"""
        ratings = user.get_ratings()
        avg_rating = user.get_average_rating()

        # Use average rating for items not rated by user
        return [ratings.get(item_id).rating if item_id in ratings else avg_rating
                for item_id in sorted(common_items)]

    def _calculate_user_similarity(self, user1: User, user2: User) -> float:
        """Calculate similarity between two users based on their ratings"""
        # Check cache first
        cache_key = tuple(sorted([user1.user_id, user2.user_id]))
        if cache_key in self._similarity_cache:
            return self._similarity_cache[cache_key]

        # Find common rated items
        user1_items = set(user1.get_ratings().keys())
        user2_items = set(user2.get_ratings().keys())
        common_items = user1_items & user2_items

        if len(common_items) < self.min_common_items:
            return 0.0

        # Get rating vectors for common items
        vector1 = self._get_user_vector(user1, common_items)
        vector2 = self._get_user_vector(user2, common_items)

        # Calculate similarity
        similarity = self.similarity_metric.calculate(vector1, vector2)

        # Cache result
        self._similarity_cache[cache_key] = similarity

        return similarity

    def _find_similar_users(self, user: User, k: int = 10) -> List[Tuple[User, float]]:
        """Find K most similar users"""
        similarities = []

        for other_user in self.users.values():
            if other_user.user_id == user.user_id:
                continue

            similarity = self._calculate_user_similarity(user, other_user)
            if similarity > 0:
                similarities.append((other_user, similarity))

        # Sort by similarity (descending) and return top K
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

    def _predict_rating(self, user: User, item_id: str,
                       similar_users: List[Tuple[User, float]]) -> float:
        """Predict rating for an item based on similar users"""
        numerator = 0.0
        denominator = 0.0

        for similar_user, similarity in similar_users:
            rating = similar_user.get_rating(item_id)
            if rating:
                numerator += similarity * rating.rating
                denominator += abs(similarity)

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def recommend(self, user: User, n: int = 10,
                 exclude_rated: bool = True) -> List[Tuple[Item, float]]:
        """Generate recommendations using collaborative filtering"""
        # Find similar users
        similar_users = self._find_similar_users(user, k=20)

        if not similar_users:
            # Cold start: return popular items
            return self._get_popular_items(user, n, exclude_rated)

        # Get items rated by similar users
        candidate_items = set()
        for similar_user, _ in similar_users:
            candidate_items.update(similar_user.get_ratings().keys())

        # Exclude items already rated by user if requested
        if exclude_rated:
            user_rated_items = set(user.get_ratings().keys())
            candidate_items -= user_rated_items

        # Predict ratings for candidate items
        predictions = []
        for item_id in candidate_items:
            if item_id in self.items:
                predicted_rating = self._predict_rating(user, item_id, similar_users)
                if predicted_rating > 0:
                    predictions.append((self.items[item_id], predicted_rating))

        # Sort by predicted rating (descending) and return top N
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n]

    def _get_popular_items(self, user: User, n: int,
                          exclude_rated: bool) -> List[Tuple[Item, float]]:
        """Fallback: return popular items"""
        popular = []
        user_rated_items = set(user.get_ratings().keys()) if exclude_rated else set()

        for item in self.items.values():
            if item.item_id not in user_rated_items:
                avg_rating = item.get_average_rating()
                rating_count = item.get_rating_count()
                # Score based on average rating and popularity
                score = avg_rating * math.log(rating_count + 1)
                popular.append((item, score))

        popular.sort(key=lambda x: x[1], reverse=True)
        return popular[:n]

    def explain_recommendation(self, user: User, item: Item) -> str:
        """Explain why item was recommended"""
        similar_users = self._find_similar_users(user, k=5)

        if not similar_users:
            return f"Recommended because '{item.title}' is popular among all users"

        # Find similar users who rated this item highly
        recommenders = []
        for similar_user, similarity in similar_users:
            rating = similar_user.get_rating(item.item_id)
            if rating and rating.rating >= 4.0:
                recommenders.append((similar_user, similarity, rating.rating))

        if recommenders:
            top_recommender = recommenders[0]
            return (f"Recommended because users similar to you "
                   f"(like {top_recommender[0].name}) rated '{item.title}' highly "
                   f"({top_recommender[2]:.1f} stars)")

        return f"Recommended based on preferences of users similar to you"


class ContentBasedFilteringStrategy(RecommendationStrategy):
    """Content-based filtering recommendation strategy"""

    def __init__(self, users: Dict[str, User], items: Dict[str, Item],
                 similarity_metric: SimilarityMetric = None):
        super().__init__(users, items)
        self.similarity_metric = similarity_metric or CosineSimilarity()

    def _build_user_profile(self, user: User) -> Dict[str, float]:
        """Build user profile based on rated items"""
        profile: Dict[str, float] = defaultdict(float)
        ratings = user.get_ratings()

        if not ratings:
            return profile

        total_weight = 0.0

        for item_id, rating in ratings.items():
            if item_id not in self.items:
                continue

            item = self.items[item_id]
            weight = rating.rating  # Use rating as weight

            # Add item features to profile (weighted)
            for feature_name, feature_value in item.features.items():
                profile[feature_name] += feature_value * weight

            total_weight += weight

        # Normalize by total weight
        if total_weight > 0:
            profile = {k: v / total_weight for k, v in profile.items()}

        return dict(profile)

    def _get_profile_vector(self, profile: Dict[str, float],
                           all_features: List[str]) -> List[float]:
        """Convert profile to vector using all features"""
        return [profile.get(feature, 0.0) for feature in all_features]

    def _get_item_vector(self, item: Item, all_features: List[str]) -> List[float]:
        """Convert item features to vector using all features"""
        return [item.features.get(feature, 0.0) for feature in all_features]

    def _calculate_item_similarity(self, user_profile: Dict[str, float],
                                  item: Item) -> float:
        """Calculate similarity between user profile and item"""
        # Get all unique features
        all_features = sorted(set(user_profile.keys()) | set(item.features.keys()))

        if not all_features:
            return 0.0

        # Convert to vectors
        profile_vector = self._get_profile_vector(user_profile, all_features)
        item_vector = self._get_item_vector(item, all_features)

        # Calculate similarity
        return self.similarity_metric.calculate(profile_vector, item_vector)

    def recommend(self, user: User, n: int = 10,
                 exclude_rated: bool = True) -> List[Tuple[Item, float]]:
        """Generate recommendations using content-based filtering"""
        # Build user profile from rated items
        user_profile = self._build_user_profile(user)

        if not user_profile:
            # Cold start: return items matching user preferences
            return self._recommend_by_preferences(user, n, exclude_rated)

        # Calculate similarity with all items
        recommendations = []
        user_rated_items = set(user.get_ratings().keys()) if exclude_rated else set()

        for item in self.items.values():
            if item.item_id in user_rated_items:
                continue

            similarity = self._calculate_item_similarity(user_profile, item)
            if similarity > 0:
                recommendations.append((item, similarity))

        # Sort by similarity (descending) and return top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:n]

    def _recommend_by_preferences(self, user: User, n: int,
                                 exclude_rated: bool) -> List[Tuple[Item, float]]:
        """Recommend items based on user preferences"""
        recommendations = []
        user_rated_items = set(user.get_ratings().keys()) if exclude_rated else set()

        for item in self.items.values():
            if item.item_id in user_rated_items:
                continue

            # Score based on tag overlap with preferences
            tag_overlap = len(item.tags & user.preferences)
            if tag_overlap > 0 or item.category in user.preferences:
                score = tag_overlap + (1 if item.category in user.preferences else 0)
                recommendations.append((item, float(score)))

        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:n]

    def explain_recommendation(self, user: User, item: Item) -> str:
        """Explain why item was recommended"""
        user_profile = self._build_user_profile(user)

        if not user_profile:
            common_tags = item.tags & user.preferences
            if common_tags:
                return f"Recommended because you're interested in: {', '.join(list(common_tags)[:3])}"
            return f"Recommended because of your interest in {item.category}"

        # Find matching features
        matching_features = []
        for feature in item.features.keys():
            if feature in user_profile and user_profile[feature] > 0:
                matching_features.append(feature)

        if matching_features:
            return (f"Recommended because '{item.title}' matches your preferences "
                   f"in: {', '.join(matching_features[:3])}")

        return f"Recommended based on items you've liked in the past"


class HybridRecommendationStrategy(RecommendationStrategy):
    """Hybrid recommendation strategy combining multiple strategies"""

    def __init__(self, users: Dict[str, User], items: Dict[str, Item],
                 strategies: List[Tuple[RecommendationStrategy, float]]):
        """
        Initialize with list of (strategy, weight) tuples
        Weights should sum to 1.0
        """
        super().__init__(users, items)
        self.strategies = strategies

        # Validate weights
        total_weight = sum(weight for _, weight in strategies)
        if not math.isclose(total_weight, 1.0, rel_tol=1e-5):
            raise ValueError(f"Strategy weights must sum to 1.0, got {total_weight}")

    def recommend(self, user: User, n: int = 10,
                 exclude_rated: bool = True) -> List[Tuple[Item, float]]:
        """Generate hybrid recommendations by combining multiple strategies"""
        # Get recommendations from all strategies
        all_recommendations: Dict[str, float] = defaultdict(float)

        for strategy, weight in self.strategies:
            strategy_recs = strategy.recommend(user, n=n*2, exclude_rated=exclude_rated)

            for item, score in strategy_recs:
                # Normalize score to 0-1 range (assuming scores are already normalized)
                normalized_score = score / 5.0 if score > 1.0 else score
                all_recommendations[item.item_id] += normalized_score * weight

        # Convert to list of (Item, score) tuples
        recommendations = [
            (self.items[item_id], score)
            for item_id, score in all_recommendations.items()
            if item_id in self.items
        ]

        # Sort by combined score (descending) and return top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:n]

    def explain_recommendation(self, user: User, item: Item) -> str:
        """Explain hybrid recommendation"""
        explanations = []

        for strategy, weight in self.strategies:
            if weight > 0.3:  # Only explain significant strategies
                explanation = strategy.explain_recommendation(user, item)
                explanations.append(f"{explanation} (weight: {weight:.0%})")

        return "; ".join(explanations)


# ============================================================================
# FACTORY PATTERN
# ============================================================================

class RecommendationFactory:
    """Factory for creating recommendation strategies and similarity metrics"""

    @staticmethod
    def create_strategy(strategy_type: str, users: Dict[str, User],
                       items: Dict[str, Item], **kwargs) -> RecommendationStrategy:
        """Create a recommendation strategy"""
        strategy_type = strategy_type.lower()

        if strategy_type == "collaborative":
            similarity_metric = kwargs.get('similarity_metric', CosineSimilarity())
            min_common_items = kwargs.get('min_common_items', 2)
            return CollaborativeFilteringStrategy(
                users, items, similarity_metric, min_common_items
            )

        elif strategy_type == "content_based":
            similarity_metric = kwargs.get('similarity_metric', CosineSimilarity())
            return ContentBasedFilteringStrategy(users, items, similarity_metric)

        elif strategy_type == "hybrid":
            # Create sub-strategies
            collaborative = CollaborativeFilteringStrategy(users, items)
            content_based = ContentBasedFilteringStrategy(users, items)

            # Default weights
            collab_weight = kwargs.get('collaborative_weight', 0.6)
            content_weight = kwargs.get('content_weight', 0.4)

            strategies = [
                (collaborative, collab_weight),
                (content_based, content_weight)
            ]

            return HybridRecommendationStrategy(users, items, strategies)

        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")

    @staticmethod
    def create_similarity_metric(metric_type: str) -> SimilarityMetric:
        """Create a similarity metric"""
        metric_type = metric_type.lower()

        if metric_type == "cosine":
            return CosineSimilarity()
        elif metric_type == "pearson":
            return PearsonCorrelation()
        elif metric_type == "euclidean":
            return EuclideanDistance()
        else:
            raise ValueError(f"Unknown similarity metric: {metric_type}")


# ============================================================================
# OBSERVER PATTERN
# ============================================================================

class RecommendationEvent:
    """Event that occurs in the recommendation system"""

    def __init__(self, event_type: RecommendationEventType, data: Dict):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now()


class RecommendationObserver(ABC):
    """Abstract observer for recommendation events"""

    @abstractmethod
    def update(self, event: RecommendationEvent) -> None:
        """Handle recommendation event"""
        pass


class AnalyticsObserver(RecommendationObserver):
    """Observer that logs analytics data"""

    def __init__(self):
        self.events: List[RecommendationEvent] = []
        self.metrics: Dict[str, int] = defaultdict(int)

    def update(self, event: RecommendationEvent) -> None:
        """Log analytics event"""
        self.events.append(event)
        self.metrics[event.event_type.value] += 1

        # Log to console (in production, would send to analytics service)
        print(f"[ANALYTICS] {event.event_type.value} at {event.timestamp}")

    def get_metrics(self) -> Dict[str, int]:
        """Get analytics metrics"""
        return dict(self.metrics)


class NotificationObserver(RecommendationObserver):
    """Observer that sends notifications"""

    def __init__(self):
        self.notifications: List[str] = []

    def update(self, event: RecommendationEvent) -> None:
        """Send notification based on event"""
        if event.event_type == RecommendationEventType.RECOMMENDATIONS_GENERATED:
            user_id = event.data.get('user_id')
            count = event.data.get('count', 0)
            message = f"New recommendations available for user {user_id} ({count} items)"
            self.notifications.append(message)
            print(f"[NOTIFICATION] {message}")

        elif event.event_type == RecommendationEventType.RATING_ADDED:
            user_id = event.data.get('user_id')
            item_id = event.data.get('item_id')
            print(f"[NOTIFICATION] User {user_id} rated item {item_id}")


class CacheObserver(RecommendationObserver):
    """Observer that manages cache invalidation"""

    def __init__(self):
        self.invalidation_count = 0

    def update(self, event: RecommendationEvent) -> None:
        """Invalidate cache when needed"""
        if event.event_type in [RecommendationEventType.RATING_ADDED,
                               RecommendationEventType.RATING_UPDATED]:
            self.invalidation_count += 1
            print(f"[CACHE] Invalidated cache due to {event.event_type.value}")


# ============================================================================
# RECOMMENDATION ENGINE (Main Component)
# ============================================================================

class RecommendationEngine:
    """
    Main recommendation engine that orchestrates the recommendation system
    Demonstrates: Strategy, Observer, and Factory patterns
    """

    def __init__(self):
        self.users: Dict[str, User] = {}
        self.items: Dict[str, Item] = {}
        self.ratings: List[Rating] = []
        self.strategy: Optional[RecommendationStrategy] = None
        self._observers: List[RecommendationObserver] = []

    # ========================================================================
    # User Management
    # ========================================================================

    def add_user(self, user: User) -> None:
        """Add a user to the system"""
        self.users[user.user_id] = user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)

    # ========================================================================
    # Item Management
    # ========================================================================

    def add_item(self, item: Item) -> None:
        """Add an item to the system"""
        self.items[item.item_id] = item

    def get_item(self, item_id: str) -> Optional[Item]:
        """Get item by ID"""
        return self.items.get(item_id)

    # ========================================================================
    # Rating Management
    # ========================================================================

    def add_rating(self, user_id: str, item_id: str, rating_value: float) -> Rating:
        """Add or update a rating"""
        # Validate user and item exist
        user = self.get_user(user_id)
        item = self.get_item(item_id)

        if not user:
            raise ValueError(f"User {user_id} not found")
        if not item:
            raise ValueError(f"Item {item_id} not found")

        # Create rating
        rating = Rating(user_id, item_id, rating_value)

        # Update user and item
        user.add_rating(rating)
        item.add_rating(rating)
        self.ratings.append(rating)

        # Notify observers
        event = RecommendationEvent(
            RecommendationEventType.RATING_ADDED,
            {'user_id': user_id, 'item_id': item_id, 'rating': rating_value}
        )
        self._notify_observers(event)

        return rating

    # ========================================================================
    # Strategy Management
    # ========================================================================

    def set_strategy(self, strategy: RecommendationStrategy) -> None:
        """Set the recommendation strategy (Strategy Pattern)"""
        self.strategy = strategy

        # Notify observers
        event = RecommendationEvent(
            RecommendationEventType.STRATEGY_CHANGED,
            {'strategy': strategy.__class__.__name__}
        )
        self._notify_observers(event)

    # ========================================================================
    # Recommendation Generation
    # ========================================================================

    def recommend(self, user_id: str, n: int = 10,
                 exclude_rated: bool = True) -> List[Tuple[Item, float]]:
        """
        Generate recommendations for a user

        Args:
            user_id: User to generate recommendations for
            n: Number of recommendations
            exclude_rated: Whether to exclude already rated items

        Returns:
            List of (Item, score) tuples
        """
        if not self.strategy:
            raise RuntimeError("No recommendation strategy set")

        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Generate recommendations
        recommendations = self.strategy.recommend(user, n, exclude_rated)

        # Notify observers
        event = RecommendationEvent(
            RecommendationEventType.RECOMMENDATIONS_GENERATED,
            {'user_id': user_id, 'count': len(recommendations)}
        )
        self._notify_observers(event)

        return recommendations

    def explain_recommendation(self, user_id: str, item_id: str) -> str:
        """Get explanation for why an item was recommended"""
        if not self.strategy:
            raise RuntimeError("No recommendation strategy set")

        user = self.get_user(user_id)
        item = self.get_item(item_id)

        if not user or not item:
            raise ValueError("User or item not found")

        return self.strategy.explain_recommendation(user, item)

    # ========================================================================
    # Observer Pattern Methods
    # ========================================================================

    def attach_observer(self, observer: RecommendationObserver) -> None:
        """Attach an observer"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach_observer(self, observer: RecommendationObserver) -> None:
        """Detach an observer"""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self, event: RecommendationEvent) -> None:
        """Notify all observers of an event"""
        for observer in self._observers:
            observer.update(event)

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def get_statistics(self) -> Dict:
        """Get system statistics"""
        return {
            'total_users': len(self.users),
            'total_items': len(self.items),
            'total_ratings': len(self.ratings),
            'average_ratings_per_user': (
                len(self.ratings) / len(self.users) if self.users else 0
            ),
            'average_ratings_per_item': (
                len(self.ratings) / len(self.items) if self.items else 0
            ),
            'strategy': self.strategy.__class__.__name__ if self.strategy else None
        }


# ============================================================================
# DEMO AND TEST SCENARIOS
# ============================================================================

def demo_recommendation_system():
    """Comprehensive demo of the recommendation system"""

    print("=" * 80)
    print("RECOMMENDATION SYSTEM DEMO")
    print("=" * 80)
    print()

    # ========================================================================
    # 1. Initialize System
    # ========================================================================
    print("1. Initializing Recommendation Engine...")
    engine = RecommendationEngine()

    # Attach observers
    analytics = AnalyticsObserver()
    notifications = NotificationObserver()
    cache = CacheObserver()

    engine.attach_observer(analytics)
    engine.attach_observer(notifications)
    engine.attach_observer(cache)
    print("   ✓ Observers attached (Analytics, Notifications, Cache)")
    print()

    # ========================================================================
    # 2. Create Users
    # ========================================================================
    print("2. Creating Users...")
    users_data = [
        ("u1", "Alice", "alice@example.com", {"action", "sci-fi"}, {}),
        ("u2", "Bob", "bob@example.com", {"comedy", "drama"}, {}),
        ("u3", "Charlie", "charlie@example.com", {"sci-fi", "thriller"}, {}),
        ("u4", "Diana", "diana@example.com", {"romance", "drama"}, {}),
        ("u5", "Eve", "eve@example.com", {"action", "thriller"}, {}),
    ]

    for user_id, name, email, preferences, demographics in users_data:
        user = User(user_id, name, email)
        for pref in preferences:
            user.add_preference(pref)
        user.demographics = demographics
        engine.add_user(user)
        print(f"   ✓ Added {user}")
    print()

    # ========================================================================
    # 3. Create Items (Movies)
    # ========================================================================
    print("3. Creating Items (Movies)...")
    movies_data = [
        ("m1", "The Matrix", "sci-fi", {"action", "sci-fi", "cyberpunk"},
         {"action": 0.9, "scifi": 0.95, "drama": 0.3}),
        ("m2", "Inception", "sci-fi", {"action", "sci-fi", "thriller"},
         {"action": 0.8, "scifi": 0.9, "drama": 0.5}),
        ("m3", "The Godfather", "drama", {"drama", "crime"},
         {"action": 0.4, "scifi": 0.0, "drama": 0.98}),
        ("m4", "Die Hard", "action", {"action", "thriller"},
         {"action": 0.95, "scifi": 0.1, "drama": 0.2}),
        ("m5", "The Notebook", "romance", {"romance", "drama"},
         {"action": 0.0, "scifi": 0.0, "drama": 0.9}),
        ("m6", "Interstellar", "sci-fi", {"sci-fi", "drama"},
         {"action": 0.3, "scifi": 0.95, "drama": 0.7}),
        ("m7", "The Hangover", "comedy", {"comedy"},
         {"action": 0.2, "scifi": 0.0, "drama": 0.3}),
        ("m8", "Blade Runner", "sci-fi", {"sci-fi", "thriller", "cyberpunk"},
         {"action": 0.6, "scifi": 0.98, "drama": 0.4}),
    ]

    for item_id, title, category, tags, features in movies_data:
        item = Item(item_id, title, category)
        for tag in tags:
            item.add_tag(tag)
        for feature_name, value in features.items():
            item.add_feature(feature_name, value)
        engine.add_item(item)
        print(f"   ✓ Added {item}")
    print()

    # ========================================================================
    # 4. Add Ratings
    # ========================================================================
    print("4. Adding User Ratings...")
    ratings_data = [
        # Alice likes action and sci-fi
        ("u1", "m1", 5.0), ("u1", "m2", 4.5), ("u1", "m4", 4.0),
        # Bob likes comedy and drama
        ("u2", "m3", 5.0), ("u2", "m7", 4.5), ("u2", "m5", 4.0),
        # Charlie likes sci-fi and thriller
        ("u3", "m1", 4.5), ("u3", "m2", 5.0), ("u3", "m8", 4.5),
        # Diana likes romance and drama
        ("u4", "m3", 4.0), ("u4", "m5", 5.0), ("u4", "m6", 3.5),
        # Eve likes action and thriller
        ("u5", "m4", 5.0), ("u5", "m2", 4.0), ("u5", "m8", 4.5),
    ]

    for user_id, item_id, rating in ratings_data:
        engine.add_rating(user_id, item_id, rating)

    print(f"   ✓ Added {len(ratings_data)} ratings")
    print()

    # ========================================================================
    # 5. Display Statistics
    # ========================================================================
    print("5. System Statistics:")
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()

    # ========================================================================
    # 6. Test Collaborative Filtering
    # ========================================================================
    print("6. Testing Collaborative Filtering Strategy...")
    print("-" * 80)

    collab_strategy = RecommendationFactory.create_strategy(
        "collaborative", engine.users, engine.items
    )
    engine.set_strategy(collab_strategy)

    # Get recommendations for Alice
    print("\n   Recommendations for Alice (Collaborative Filtering):")
    alice_recs = engine.recommend("u1", n=3)
    for i, (item, score) in enumerate(alice_recs, 1):
        explanation = engine.explain_recommendation("u1", item.item_id)
        print(f"   {i}. {item.title} (score: {score:.3f})")
        print(f"      → {explanation}")
    print()

    # ========================================================================
    # 7. Test Content-Based Filtering
    # ========================================================================
    print("7. Testing Content-Based Filtering Strategy...")
    print("-" * 80)

    content_strategy = RecommendationFactory.create_strategy(
        "content_based", engine.users, engine.items
    )
    engine.set_strategy(content_strategy)

    # Get recommendations for Alice
    print("\n   Recommendations for Alice (Content-Based Filtering):")
    alice_recs = engine.recommend("u1", n=3)
    for i, (item, score) in enumerate(alice_recs, 1):
        explanation = engine.explain_recommendation("u1", item.item_id)
        print(f"   {i}. {item.title} (score: {score:.3f})")
        print(f"      → {explanation}")
    print()

    # ========================================================================
    # 8. Test Hybrid Strategy
    # ========================================================================
    print("8. Testing Hybrid Recommendation Strategy...")
    print("-" * 80)

    hybrid_strategy = RecommendationFactory.create_strategy(
        "hybrid", engine.users, engine.items,
        collaborative_weight=0.6, content_weight=0.4
    )
    engine.set_strategy(hybrid_strategy)

    # Get recommendations for multiple users
    print("\n   Recommendations for All Users (Hybrid Strategy):")
    for user_id in ["u1", "u2", "u3"]:
        user = engine.get_user(user_id)
        print(f"\n   {user.name}:")
        recs = engine.recommend(user_id, n=3)
        for i, (item, score) in enumerate(recs, 1):
            print(f"      {i}. {item.title} (score: {score:.3f})")
    print()

    # ========================================================================
    # 9. Test Different Similarity Metrics
    # ========================================================================
    print("9. Testing Different Similarity Metrics...")
    print("-" * 80)

    metrics = [
        ("Cosine Similarity", CosineSimilarity()),
        ("Pearson Correlation", PearsonCorrelation()),
        ("Euclidean Distance", EuclideanDistance()),
    ]

    for metric_name, metric in metrics:
        print(f"\n   Using {metric_name}:")
        strategy = RecommendationFactory.create_strategy(
            "collaborative", engine.users, engine.items,
            similarity_metric=metric
        )
        engine.set_strategy(strategy)

        recs = engine.recommend("u1", n=2)
        for i, (item, score) in enumerate(recs, 1):
            print(f"      {i}. {item.title} (score: {score:.3f})")
    print()

    # ========================================================================
    # 10. Display Observer Metrics
    # ========================================================================
    print("10. Observer Analytics:")
    print("-" * 80)
    print(f"   Analytics Metrics: {analytics.get_metrics()}")
    print(f"   Cache Invalidations: {cache.invalidation_count}")
    print(f"   Notifications Sent: {len(notifications.notifications)}")
    print()

    # ========================================================================
    # 11. Test Edge Cases
    # ========================================================================
    print("11. Testing Edge Cases...")
    print("-" * 80)

    # New user with no ratings
    new_user = User("u6", "Frank", "frank@example.com")
    new_user.add_preference("action")
    engine.add_user(new_user)

    print("\n   Recommendations for new user (cold start):")
    strategy = RecommendationFactory.create_strategy(
        "collaborative", engine.users, engine.items
    )
    engine.set_strategy(strategy)

    new_user_recs = engine.recommend("u6", n=3)
    for i, (item, score) in enumerate(new_user_recs, 1):
        print(f"      {i}. {item.title} (score: {score:.3f})")
    print()

    print("=" * 80)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nDesign Patterns Demonstrated:")
    print("✓ Strategy Pattern: Multiple recommendation algorithms")
    print("✓ Factory Pattern: Creating strategies and similarity metrics")
    print("✓ Observer Pattern: Analytics, notifications, and cache management")
    print("\nSOLID Principles Followed:")
    print("✓ Single Responsibility: Each class has one clear purpose")
    print("✓ Open/Closed: Easy to add new strategies without modifying existing code")
    print("✓ Liskov Substitution: All strategies are interchangeable")
    print("✓ Interface Segregation: Clean, focused interfaces")
    print("✓ Dependency Inversion: Depend on abstractions, not concretions")
    print()


if __name__ == "__main__":
    demo_recommendation_system()
