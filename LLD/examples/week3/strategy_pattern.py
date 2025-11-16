"""
Strategy Pattern - Define a family of algorithms, encapsulate each one, and make them interchangeable.

This module demonstrates various strategy implementations:
1. Payment strategies with different payment methods
2. Sorting algorithms as strategies
3. Compression algorithms as strategies
4. Route calculation strategies
5. Strategy factory for dynamic selection
6. Configuration-based strategy selection

Key Learning Points:
- Strategy pattern allows algorithm selection at runtime
- Each algorithm is encapsulated in its own class
- Client uses strategies through common interface
- Easy to add new strategies without modifying existing code
- Excellent alternative to complex if/else chains
- Works well with factory pattern for strategy creation
"""

from abc import ABC, abstractmethod
from typing import List, Any, Callable
from enum import Enum
import time


# ============================================================================
# 1. PAYMENT STRATEGY EXAMPLE
# ============================================================================

class PaymentStrategy(ABC):
    """Abstract strategy for payment processing."""

    @abstractmethod
    def pay(self, amount: float) -> bool:
        """Process payment with this strategy."""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate payment method."""
        pass


class CreditCardPayment(PaymentStrategy):
    """Strategy for credit card payment."""

    def __init__(self, card_number: str, cvv: str, expiry: str):
        self.card_number = card_number
        self.cvv = cvv
        self.expiry = expiry

    def validate(self) -> bool:
        """Validate credit card details."""
        # Simple validation
        if len(self.card_number) < 13 or len(self.cvv) != 3:
            return False
        return True

    def pay(self, amount: float) -> bool:
        """Process credit card payment."""
        if not self.validate():
            print(f"Invalid credit card")
            return False
        print(f"Processing credit card payment of ${amount:.2f}")
        print(f"Card: {self.card_number[-4:]} (XXXX-XXXX-XXXX-{self.card_number[-4:]})")
        print(f"Payment successful!")
        return True


class PayPalPayment(PaymentStrategy):
    """Strategy for PayPal payment."""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def validate(self) -> bool:
        """Validate PayPal account."""
        if "@" not in self.email or len(self.password) < 6:
            return False
        return True

    def pay(self, amount: float) -> bool:
        """Process PayPal payment."""
        if not self.validate():
            print(f"Invalid PayPal credentials")
            return False
        print(f"Processing PayPal payment of ${amount:.2f}")
        print(f"Email: {self.email}")
        print(f"Authenticating with PayPal...")
        print(f"Payment successful!")
        return True


class CryptocurrencyPayment(PaymentStrategy):
    """Strategy for cryptocurrency payment."""

    def __init__(self, wallet_address: str, coin_type: str = "BTC"):
        self.wallet_address = wallet_address
        self.coin_type = coin_type

    def validate(self) -> bool:
        """Validate cryptocurrency wallet."""
        if len(self.wallet_address) < 20:
            return False
        return True

    def pay(self, amount: float) -> bool:
        """Process cryptocurrency payment."""
        if not self.validate():
            print(f"Invalid wallet address")
            return False
        print(f"Processing {self.coin_type} payment of {amount:.8f}")
        print(f"Wallet: {self.wallet_address}")
        print(f"Confirming transaction on blockchain...")
        print(f"Payment successful!")
        return True


class ApplePayPayment(PaymentStrategy):
    """Strategy for Apple Pay payment."""

    def __init__(self, device_id: str, token: str):
        self.device_id = device_id
        self.token = token

    def validate(self) -> bool:
        """Validate Apple Pay token."""
        return len(self.token) > 10

    def pay(self, amount: float) -> bool:
        """Process Apple Pay payment."""
        if not self.validate():
            print(f"Invalid Apple Pay token")
            return False
        print(f"Processing Apple Pay payment of ${amount:.2f}")
        print(f"Device: {self.device_id}")
        print(f"Biometric authentication confirmed")
        print(f"Payment successful!")
        return True


# ============================================================================
# 2. SORTING STRATEGY EXAMPLE
# ============================================================================

class SortingStrategy(ABC):
    """Abstract strategy for sorting."""

    @abstractmethod
    def sort(self, arr: List[int]) -> List[int]:
        """Sort array using this strategy."""
        pass


class BubbleSortStrategy(SortingStrategy):
    """Strategy for bubble sort."""

    def sort(self, arr: List[int]) -> List[int]:
        """Sort using bubble sort - simple but slow for large arrays."""
        arr = arr.copy()
        n = len(arr)
        comparisons = 0
        swaps = 0

        for i in range(n):
            for j in range(0, n - i - 1):
                comparisons += 1
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swaps += 1

        print(f"Bubble Sort: Comparisons={comparisons}, Swaps={swaps}")
        return arr


class QuickSortStrategy(SortingStrategy):
    """Strategy for quick sort."""

    def sort(self, arr: List[int]) -> List[int]:
        """Sort using quick sort - fast for average case."""
        arr = arr.copy()

        def quick_sort(arr, low, high, stats):
            if low < high:
                pi = self._partition(arr, low, high, stats)
                quick_sort(arr, low, pi - 1, stats)
                quick_sort(arr, pi + 1, high, stats)
            return arr

        def partition(arr, low, high):
            pivot = arr[high]
            i = low - 1
            comparisons = [0]

            for j in range(low, high):
                comparisons[0] += 1
                if arr[j] < pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]

            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            return i + 1, comparisons[0]

        stats = {"comparisons": 0}
        result = quick_sort(arr, 0, len(arr) - 1, stats)
        print(f"Quick Sort: Comparisons~{len(arr) * 5}")
        return result

    def _partition(self, arr, low, high, stats):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            if arr[j] < pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1


class MergeSortStrategy(SortingStrategy):
    """Strategy for merge sort."""

    def sort(self, arr: List[int]) -> List[int]:
        """Sort using merge sort - stable and consistent O(n log n)."""
        arr = arr.copy()

        def merge_sort(arr):
            if len(arr) <= 1:
                return arr

            mid = len(arr) // 2
            left = merge_sort(arr[:mid])
            right = merge_sort(arr[mid:])
            return self._merge(left, right)

        result = merge_sort(arr)
        print(f"Merge Sort: O(n log n) guaranteed")
        return result

    def _merge(self, left, right):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result


# ============================================================================
# 3. COMPRESSION STRATEGY EXAMPLE
# ============================================================================

class CompressionStrategy(ABC):
    """Abstract strategy for compression."""

    @abstractmethod
    def compress(self, data: str) -> str:
        """Compress data using this strategy."""
        pass

    @abstractmethod
    def decompress(self, data: str) -> str:
        """Decompress data using this strategy."""
        pass


class ZipCompressionStrategy(CompressionStrategy):
    """Strategy for ZIP compression (simulated)."""

    def compress(self, data: str) -> str:
        """Compress using ZIP format."""
        # Simulated compression
        compressed = "ZIP:" + data[:len(data)//2]  # Simulated
        print(f"ZIP Compression: {len(data)} -> {len(compressed)} bytes")
        return compressed

    def decompress(self, data: str) -> str:
        """Decompress ZIP data."""
        if not data.startswith("ZIP:"):
            return data
        # Simulated decompression
        return data[4:] + data[4:]


class RarCompressionStrategy(CompressionStrategy):
    """Strategy for RAR compression (simulated)."""

    def compress(self, data: str) -> str:
        """Compress using RAR format."""
        compressed = "RAR:" + data[:len(data)//3]  # More compression
        print(f"RAR Compression: {len(data)} -> {len(compressed)} bytes")
        return compressed

    def decompress(self, data: str) -> str:
        """Decompress RAR data."""
        if not data.startswith("RAR:"):
            return data
        return data[4:] + data[4:] + data[4:]


class SevenZipCompressionStrategy(CompressionStrategy):
    """Strategy for 7z compression (simulated)."""

    def compress(self, data: str) -> str:
        """Compress using 7z format."""
        compressed = "7Z:" + data[:len(data)//4]  # Best compression
        print(f"7Z Compression: {len(data)} -> {len(compressed)} bytes")
        return compressed

    def decompress(self, data: str) -> str:
        """Decompress 7z data."""
        if not data.startswith("7Z:"):
            return data
        return data[3:] + data[3:] + data[3:] + data[3:]


# ============================================================================
# 4. ROUTE CALCULATION STRATEGY
# ============================================================================

class RouteStrategy(ABC):
    """Abstract strategy for route calculation."""

    @abstractmethod
    def calculate_route(self, start: str, end: str) -> dict:
        """Calculate route from start to end."""
        pass


class FastestRouteStrategy(RouteStrategy):
    """Strategy for fastest route (highways)."""

    def calculate_route(self, start: str, end: str) -> dict:
        return {
            "route": f"{start} -> Highway 1 -> {end}",
            "distance": 150,
            "time_minutes": 120,
            "toll": 15.50
        }


class ShortestRouteStrategy(RouteStrategy):
    """Strategy for shortest route (direct path)."""

    def calculate_route(self, start: str, end: str) -> dict:
        return {
            "route": f"{start} -> Direct Path -> {end}",
            "distance": 100,
            "time_minutes": 180,
            "toll": 0
        }


class EconomyRouteStrategy(RouteStrategy):
    """Strategy for economy route (minimize cost)."""

    def calculate_route(self, start: str, end: str) -> dict:
        return {
            "route": f"{start} -> Local Roads -> {end}",
            "distance": 120,
            "time_minutes": 240,
            "toll": 0
        }


class ScenicRouteStrategy(RouteStrategy):
    """Strategy for scenic route (maximize experience)."""

    def calculate_route(self, start: str, end: str) -> dict:
        return {
            "route": f"{start} -> Scenic Route -> {end}",
            "distance": 180,
            "time_minutes": 300,
            "toll": 0
        }


# ============================================================================
# 5. CONTEXT CLASS
# ============================================================================

class PaymentProcessor:
    """Context class that uses payment strategies."""

    def __init__(self, strategy: PaymentStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: PaymentStrategy):
        """Change payment strategy at runtime."""
        self._strategy = strategy

    def process_payment(self, amount: float) -> bool:
        """Process payment using configured strategy."""
        print(f"\n{'='*50}")
        print(f"Processing payment of ${amount:.2f}")
        print(f"Using: {self._strategy.__class__.__name__}")
        print(f"{'='*50}")
        return self._strategy.pay(amount)


class Sorter:
    """Context class that uses sorting strategies."""

    def __init__(self, strategy: SortingStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SortingStrategy):
        """Change sorting strategy."""
        self._strategy = strategy

    def sort(self, arr: List[int]) -> List[int]:
        """Sort array using configured strategy."""
        return self._strategy.sort(arr)


class Navigator:
    """Context class that uses route strategies."""

    def __init__(self, strategy: RouteStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: RouteStrategy):
        """Change route strategy."""
        self._strategy = strategy

    def navigate(self, start: str, end: str) -> dict:
        """Navigate from start to end using configured strategy."""
        return self._strategy.calculate_route(start, end)


# ============================================================================
# 6. STRATEGY FACTORY
# ============================================================================

class PaymentStrategyFactory:
    """Factory for creating payment strategies."""

    @staticmethod
    def create_strategy(strategy_type: str, **kwargs) -> PaymentStrategy:
        """Create payment strategy based on type."""
        strategies = {
            "credit_card": CreditCardPayment,
            "paypal": PayPalPayment,
            "crypto": CryptocurrencyPayment,
            "apple_pay": ApplePayPayment,
        }

        strategy_class = strategies.get(strategy_type.lower())
        if not strategy_class:
            raise ValueError(f"Unknown strategy: {strategy_type}")

        return strategy_class(**kwargs)


class SortingStrategyFactory:
    """Factory for creating sorting strategies."""

    @staticmethod
    def create_strategy(strategy_type: str) -> SortingStrategy:
        """Create sorting strategy based on type."""
        strategies = {
            "bubble": BubbleSortStrategy,
            "quick": QuickSortStrategy,
            "merge": MergeSortStrategy,
        }

        strategy_class = strategies.get(strategy_type.lower())
        if not strategy_class:
            raise ValueError(f"Unknown strategy: {strategy_type}")

        return strategy_class()


# ============================================================================
# 7. DEMONSTRATION
# ============================================================================

def demo_payment_strategies():
    """Demonstrate payment strategies."""
    print("\n" + "="*60)
    print("STRATEGY PATTERN - PAYMENT EXAMPLE")
    print("="*60)

    # Create processor with credit card
    processor = PaymentProcessor(
        CreditCardPayment("1234567890123", "123", "12/25")
    )

    # Process payment
    processor.process_payment(100.00)

    # Switch to PayPal
    processor.set_strategy(
        PayPalPayment("user@example.com", "password123")
    )
    processor.process_payment(50.00)

    # Switch to Cryptocurrency
    processor.set_strategy(
        CryptocurrencyPayment("1A1z7agoat2Bt89ZqNQrWNIP5PePpzMSwJ", "BTC")
    )
    processor.process_payment(0.005)

    # Switch to Apple Pay
    processor.set_strategy(
        ApplePayPayment("iPhone13", "applepay_token_12345")
    )
    processor.process_payment(75.50)

    # Using factory
    print("\n" + "-"*60)
    print("Using Strategy Factory:")
    print("-"*60)

    strategy = PaymentStrategyFactory.create_strategy(
        "paypal",
        email="john@example.com",
        password="secure_pass"
    )
    processor.set_strategy(strategy)
    processor.process_payment(150.00)


def demo_sorting_strategies():
    """Demonstrate sorting strategies."""
    print("\n" + "="*60)
    print("STRATEGY PATTERN - SORTING EXAMPLE")
    print("="*60)

    arr = [64, 34, 25, 12, 22, 11, 90]
    print(f"\nOriginal array: {arr}")

    sorter = Sorter(BubbleSortStrategy())
    print(f"Bubble Sort result: {sorter.sort(arr)}")

    sorter.set_strategy(QuickSortStrategy())
    print(f"Quick Sort result: {sorter.sort(arr)}")

    sorter.set_strategy(MergeSortStrategy())
    print(f"Merge Sort result: {sorter.sort(arr)}")

    # Factory
    print("\n" + "-"*60)
    print("Using Strategy Factory:")
    print("-"*60)

    strategy = SortingStrategyFactory.create_strategy("merge")
    sorter.set_strategy(strategy)
    print(f"Factory-created Merge Sort: {sorter.sort(arr)}")


def demo_compression_strategies():
    """Demonstrate compression strategies."""
    print("\n" + "="*60)
    print("STRATEGY PATTERN - COMPRESSION EXAMPLE")
    print("="*60)

    data = "This is a sample text that will be compressed using different strategies."
    print(f"\nOriginal data ({len(data)} bytes): {data[:50]}...")

    # ZIP
    compressor = ZipCompressionStrategy()
    compressed = compressor.compress(data)
    decompressed = compressor.decompress(compressed)
    print(f"ZIP compressed and decompressed")

    # RAR
    compressor = RarCompressionStrategy()
    compressed = compressor.compress(data)
    decompressed = compressor.decompress(compressed)
    print(f"RAR compressed and decompressed")

    # 7Z
    compressor = SevenZipCompressionStrategy()
    compressed = compressor.compress(data)
    decompressed = compressor.decompress(compressed)
    print(f"7Z compressed and decompressed (best compression)")


def demo_route_strategies():
    """Demonstrate route strategies."""
    print("\n" + "="*60)
    print("STRATEGY PATTERN - ROUTE CALCULATION EXAMPLE")
    print("="*60)

    navigator = Navigator(FastestRouteStrategy())

    start, end = "New York", "Boston"

    print(f"\nNavigating from {start} to {end}")
    print("\n" + "-"*60)

    # Fastest route
    navigator.set_strategy(FastestRouteStrategy())
    route = navigator.navigate(start, end)
    print(f"FASTEST ROUTE:")
    print(f"  Route: {route['route']}")
    print(f"  Distance: {route['distance']} miles")
    print(f"  Time: {route['time_minutes']} minutes")
    print(f"  Toll: ${route['toll']}")

    # Shortest route
    navigator.set_strategy(ShortestRouteStrategy())
    route = navigator.navigate(start, end)
    print(f"\nSHORTEST ROUTE:")
    print(f"  Route: {route['route']}")
    print(f"  Distance: {route['distance']} miles")
    print(f"  Time: {route['time_minutes']} minutes")
    print(f"  Toll: ${route['toll']}")

    # Economy route
    navigator.set_strategy(EconomyRouteStrategy())
    route = navigator.navigate(start, end)
    print(f"\nECONOMY ROUTE:")
    print(f"  Route: {route['route']}")
    print(f"  Distance: {route['distance']} miles")
    print(f"  Time: {route['time_minutes']} minutes")
    print(f"  Toll: ${route['toll']}")

    # Scenic route
    navigator.set_strategy(ScenicRouteStrategy())
    route = navigator.navigate(start, end)
    print(f"\nSCENIC ROUTE:")
    print(f"  Route: {route['route']}")
    print(f"  Distance: {route['distance']} miles")
    print(f"  Time: {route['time_minutes']} minutes")
    print(f"  Toll: ${route['toll']}")


def demo_strategy_comparison():
    """Demonstrate strategy pattern benefits."""
    print("\n" + "="*60)
    print("STRATEGY PATTERN - BENEFITS")
    print("="*60)

    print("""
KEY BENEFITS:

1. ELIMINATES CONDITIONALS
   - Instead of: if payment_type == "credit_card": ...
   - Use: processor.set_strategy(CreditCardPayment(...))

2. OPEN/CLOSED PRINCIPLE
   - Open for extension: Add new strategies easily
   - Closed for modification: Existing code unchanged

3. SINGLE RESPONSIBILITY
   - Each strategy has one job
   - Each algorithm isolated in its own class

4. RUNTIME FLEXIBILITY
   - Change algorithms at runtime
   - No recompilation needed
   - Dynamic selection based on conditions

5. EASY TESTING
   - Test each strategy independently
   - Mock strategies for testing client code

6. CODE REUSABILITY
   - Reuse same strategy in different contexts
   - Multiple clients can share same strategy

7. AVOID SUBCLASS EXPLOSION
   - Instead of CreditCardPayment, CreditCardPayPalPayment, etc.
   - Use composition to combine behaviors
    """)


# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

"""
KEY TAKEAWAYS - STRATEGY PATTERN:

1. WHEN TO USE:
   - Multiple algorithm implementations
   - Runtime algorithm selection needed
   - Complex if/else chains based on type
   - Algorithms need to be tested independently

2. DESIGN GUIDELINES:
   - Define clear strategy interface
   - Each concrete strategy implements full algorithm
   - Client uses same interface for all strategies
   - Consider factory for strategy creation

3. COMMON PITFALLS:
   - Using when simple if/else is enough
   - Over-generalizing strategy interface
   - Not providing way to switch strategies
   - Creating too many strategies

4. PATTERN INTERACTIONS:
   - Works well with Factory pattern
   - Can be combined with Decorator pattern
   - Often used with Template Method (different pattern)
   - Can use Strategy within Template Method steps

5. REAL WORLD EXAMPLES:
   - Payment processors
   - Search algorithms
   - Sorting/filtering
   - Compression/encoding
   - Route/path calculation
   - Cache replacement policies
   - Authentication mechanisms

6. COMPARE WITH ALTERNATIVES:
   - vs. Inheritance: Strategy uses composition
   - vs. If/Else: Strategy avoids conditionals
   - vs. Factory: Factory creates strategies
   - vs. State: State varies with object state, Strategy is client choice
"""


if __name__ == "__main__":
    demo_payment_strategies()
    demo_sorting_strategies()
    demo_compression_strategies()
    demo_route_strategies()
    demo_strategy_comparison()

    print("\n" + "="*60)
    print("All Strategy Pattern examples completed!")
    print("="*60)
