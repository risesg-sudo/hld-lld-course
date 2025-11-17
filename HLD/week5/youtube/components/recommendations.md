# YouTube: Recommendation Engine

## The Recommendation Challenge

With billions of videos and billions of users, computing personalized recommendations is a massive ML problem. Recommendations drive 70% of watch time, so accuracy directly impacts engagement.

## Two-Stage Architecture

**Stage 1: Candidate Generation** (narrow from billions to hundreds)
**Stage 2: Ranking** (rank top candidates)

Why two stages? Computing scores for all billion videos is too expensive. Generate candidates efficiently, then rank carefully.

## Candidate Generation

```python
def generate_candidates(user_id, count=500):
    candidates = []
    
    # 1. Collaborative filtering (users who watched A also watched B)
    similar_users = find_similar_users(user_id, limit=1000)
    for user in similar_users:
        candidates.extend(user.recent_watches[:5])
    
    # 2. Content-based (similar to what you watched)
    recent_watches = get_recent_watches(user_id, limit=20)
    for video in recent_watches:
        similar = find_similar_videos(video, limit=10)
        candidates.extend(similar)
    
    # 3. Trending in your region
    trending = get_trending_videos(user.region, limit=50)
    candidates.extend(trending)
    
    # 4. Subscribed channels' new videos
    subscriptions = get_subscriptions(user_id)
    for channel in subscriptions:
        candidates.extend(channel.recent_videos[:3])
    
    # Deduplicate and return top 500
    return list(set(candidates))[:count]
```

## Ranking Model

Deep neural network with features:
```python
features = {
    # User features
    'watch_history': last_100_videos,
    'search_history': last_50_searches,
    'age': user.age,
    'location': user.location,
    'time_of_day': current_hour,
    
    # Video features
    'title_embedding': video.title_vector,
    'category': video.category,
    'upload_date': video.uploaded_at,
    'view_count': video.views,
    'like_ratio': video.likes / video.views,
    
    # Interaction features
    'user_channel_affinity': has_watched_this_channel_before,
    'topic_match': user_interests ∩ video_topics,
}

# Model predicts probability user will watch >50% of video
score = model.predict(features)
```

## Ranking Factors

1. **Relevance** (60%): How well video matches user interests
2. **Quality** (20%): View duration, like ratio, engagement
3. **Freshness** (10%): Newer videos ranked higher
4. **Diversity** (10%): Avoid filter bubble, include varied topics

## Serving Architecture

**Batch computation** (overnight):
```python
# For each user, pre-compute recommendations
for user in all_users:
    candidates = generate_candidates(user.id, 1000)
    ranked = rank_candidates(user.id, candidates)
    cache.set(f'recommendations:{user.id}', ranked[:100])
```

**Real-time adjustment**:
```python
def get_recommendations(user_id):
    # Start with pre-computed
    base_recs = cache.get(f'recommendations:{user_id}')
    
    # Adjust based on recent activity (last hour)
    recent_watches = get_recent_watches(user_id, minutes=60)
    if recent_watches:
        # Rerank to incorporate fresh signals
        base_recs = rerank_with_recent_context(base_recs, recent_watches)
    
    return base_recs[:20]
```

## Why This Design Works

**Two stages balance accuracy and performance**: Candidate generation is fast but approximate. Ranking is expensive but accurate.

**Pre-computation enables scale**: Can't compute for 2.5B users in real-time. Pre-compute overnight, adjust real-time.

**Multiple signal sources**: Collaborative, content-based, trending, subscriptions - each catches different preferences.

**Feature-rich model**: Hundreds of features capture nuanced preferences better than simple approaches.
