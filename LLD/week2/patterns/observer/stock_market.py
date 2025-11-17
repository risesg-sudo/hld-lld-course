"""
Stock Market Observer Example

Demonstrates how observers (traders, analysts) react to subject (stock) changes.
"""

from abc import ABC, abstractmethod
from typing import List
from datetime import datetime


class StockObserver(ABC):
    """Abstract observer interface."""
    
    @abstractmethod
    def on_price_changed(self, stock: "Stock", old_price: float, new_price: float):
        """Called when stock price changes."""
        pass


class Stock:
    """
    Subject that observers watch.
    
    Notifies observers whenever price changes.
    """
    
    def __init__(self, symbol: str, price: float):
        self.symbol = symbol
        self.price = price
        self._observers: List[StockObserver] = []
    
    def attach(self, observer: StockObserver):
        """Register an observer."""
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"{observer.__class__.__name__} subscribed to {self.symbol}")
    
    def detach(self, observer: StockObserver):
        """Unregister an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"{observer.__class__.__name__} unsubscribed from {self.symbol}")
    
    def set_price(self, new_price: float):
        """Update price and notify observers."""
        old_price = self.price
        self.price = new_price
        change_pct = ((new_price - old_price) / old_price) * 100
        
        print(f"\n{self.symbol}: ${old_price:.2f} -> ${new_price:.2f} ({change_pct:+.2f}%)")
        self._notify_observers(old_price, new_price)
    
    def _notify_observers(self, old_price: float, new_price: float):
        """Notify all registered observers."""
        for observer in self._observers:
            observer.on_price_changed(self, old_price, new_price)


class Trader(StockObserver):
    """Observer that trades based on price changes."""
    
    def __init__(self, name: str, buy_threshold: float):
        self.name = name
        self.buy_threshold = buy_threshold
    
    def on_price_changed(self, stock: Stock, old_price: float, new_price: float):
        """React to price change."""
        if new_price < self.buy_threshold and new_price < old_price:
            print(f"  {self.name}: BUY signal! Price below ${self.buy_threshold:.2f}")
        elif new_price > old_price * 1.05:
            print(f"  {self.name}: SELL signal! Price up 5%+")


class Analyst(StockObserver):
    """Observer that analyzes price trends."""
    
    def __init__(self, name: str):
        self.name = name
    
    def on_price_changed(self, stock: Stock, old_price: float, new_price: float):
        """Analyze price change."""
        change_pct = ((new_price - old_price) / old_price) * 100
        
        if abs(change_pct) > 5:
            sentiment = "BULLISH" if change_pct > 0 else "BEARISH"
            print(f"  {self.name}: {sentiment} - Significant {abs(change_pct):.1f}% move")


def demonstrate():
    """Demonstrate observer pattern with stock market."""
    print("="*70)
    print("STOCK MARKET OBSERVER PATTERN")
    print("="*70)
    
    # Create stock (subject)
    apple = Stock("AAPL", 150.0)
    
    # Create observers
    trader1 = Trader("Alice", 145.0)
    trader2 = Trader("Bob", 140.0)
    analyst = Analyst("Charlie")
    
    # Register observers
    print("\n1. Registering observers:")
    apple.attach(trader1)
    apple.attach(trader2)
    apple.attach(analyst)
    
    # Price changes trigger notifications
    print("\n2. Price changes:")
    apple.set_price(148.0)  # Small drop
    apple.set_price(142.0)  # Bigger drop - triggers buy signals
    apple.set_price(152.0)  # Big jump - triggers sell signals
    
    # Unregister observer
    print("\n3. Unregistering trader1:")
    apple.detach(trader1)
    
    print("\n4. Another price change (trader1 won't be notified):")
    apple.set_price(140.0)


if __name__ == "__main__":
    demonstrate()
    
    print("\n" + "="*70)
    print("KEY POINTS")
    print("="*70)
    print("""
1. Stock (subject) doesn't know observer details
2. Observers react independently to same event
3. Can add/remove observers dynamically
4. One price change notifies all observers
5. Loose coupling between stock and observers
    """)
