"""
Observer Pattern - Define one-to-many relationships between objects.

This module demonstrates various observer implementations:
1. Simple observer pattern with Subject
2. Event-based observer system
3. Stock market ticker example
4. UI event system
5. Notification system with priorities
6. Weak reference observers (memory leak prevention)

Key Learning Points:
- Observer enables loose coupling between subjects and observers
- Subjects notify observers automatically of state changes
- Observers can subscribe/unsubscribe at runtime
- Can use push model (subject sends data) or pull model (observer requests data)
- Must prevent memory leaks by properly unsubscribing
"""

import weakref
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum


# ============================================================================
# 1. SIMPLE OBSERVER PATTERN
# ============================================================================

class Observer(ABC):
    """Abstract base class for observers."""

    @abstractmethod
    def update(self, subject: "Subject"):
        """Called when subject changes."""
        pass


class Subject:
    """
    Subject that notifies observers of state changes.

    Uses pull model - observers request data from subject when notified.
    """

    def __init__(self):
        self._observers: List[Observer] = []
        self._state = None

    def attach(self, observer: Observer):
        """Attach observer to subject."""
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"Observer {observer.__class__.__name__} attached")

    def detach(self, observer: Observer):
        """Detach observer from subject."""
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"Observer {observer.__class__.__name__} detached")

    def notify(self):
        """Notify all observers of state change."""
        for observer in self._observers:
            observer.update(self)

    @property
    def state(self):
        """Get subject state."""
        return self._state

    @state.setter
    def state(self, value):
        """Set subject state and notify observers."""
        print(f"Subject state changed to: {value}")
        self._state = value
        self.notify()


# ============================================================================
# 2. STOCK MARKET OBSERVER EXAMPLE
# ============================================================================

class Stock:
    """
    Stock with observers tracking price changes.
    """

    def __init__(self, symbol: str, initial_price: float):
        self.symbol = symbol
        self.price = initial_price
        self._observers: List["StockObserver"] = []
        self.update_history: List[tuple] = []

    def attach_observer(self, observer: "StockObserver"):
        """Attach observer to stock."""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach_observer(self, observer: "StockObserver"):
        """Detach observer from stock."""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self):
        """Notify all observers of price change."""
        for observer in self._observers:
            observer.on_stock_price_changed(self)

    def update_price(self, new_price: float):
        """
        Update stock price and notify observers.

        Uses PUSH model - subject sends current price to observers.
        """
        old_price = self.price
        self.price = new_price
        change = ((new_price - old_price) / old_price) * 100
        self.update_history.append((
            datetime.now(),
            old_price,
            new_price,
            change
        ))
        print(f"\n{self.symbol} price changed: ${old_price:.2f} -> ${new_price:.2f} ({change:+.2f}%)")
        self.notify_observers()

    def __str__(self):
        return f"Stock({self.symbol}, ${self.price:.2f})"


class StockObserver(ABC):
    """Abstract base class for stock observers."""

    @abstractmethod
    def on_stock_price_changed(self, stock: Stock):
        """Called when stock price changes."""
        pass


class StockTrader(StockObserver):
    """
    Trader observing stocks to make trading decisions.
    """

    def __init__(self, name: str, target_price: float):
        self.name = name
        self.target_price = target_price
        self.portfolio: Dict[str, int] = {}
        self.trades: List[Dict] = []

    def on_stock_price_changed(self, stock: Stock):
        """React to stock price change."""
        if stock.price <= self.target_price:
            self.buy(stock)
        elif stock.price >= self.target_price * 1.2:
            self.sell(stock)

    def buy(self, stock: Stock):
        """Buy stock."""
        quantity = 10
        self.portfolio[stock.symbol] = self.portfolio.get(stock.symbol, 0) + quantity
        self.trades.append({
            "action": "BUY",
            "symbol": stock.symbol,
            "price": stock.price,
            "quantity": quantity,
            "timestamp": datetime.now()
        })
        print(f"  Trader {self.name} BUY: {quantity} shares of {stock.symbol} @ ${stock.price:.2f}")

    def sell(self, stock: Stock):
        """Sell stock."""
        if stock.symbol in self.portfolio and self.portfolio[stock.symbol] > 0:
            quantity = self.portfolio[stock.symbol]
            self.portfolio[stock.symbol] = 0
            self.trades.append({
                "action": "SELL",
                "symbol": stock.symbol,
                "price": stock.price,
                "quantity": quantity,
                "timestamp": datetime.now()
            })
            print(f"  Trader {self.name} SELL: {quantity} shares of {stock.symbol} @ ${stock.price:.2f}")

    def __str__(self):
        return f"Trader({self.name}, target_price=${self.target_price:.2f})"


class StockAnalyst(StockObserver):
    """
    Analyst observing stocks to provide analysis.
    """

    def __init__(self, name: str):
        self.name = name
        self.analyses: List[Dict] = []

    def on_stock_price_changed(self, stock: Stock):
        """Provide analysis on stock price change."""
        # Simple analysis logic
        if len(stock.update_history) > 0:
            _, _, _, last_change = stock.update_history[-1]

            if last_change > 5:
                sentiment = "BULLISH"
            elif last_change < -5:
                sentiment = "BEARISH"
            else:
                sentiment = "NEUTRAL"

            analysis = {
                "symbol": stock.symbol,
                "price": stock.price,
                "sentiment": sentiment,
                "timestamp": datetime.now()
            }
            self.analyses.append(analysis)
            print(f"  Analyst {self.name} says {stock.symbol} is {sentiment}")


# ============================================================================
# 3. EVENT-BASED OBSERVER SYSTEM
# ============================================================================

class Event:
    """Represents an event with data."""

    def __init__(self, event_type: str, data: Any = None):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now()

    def __str__(self):
        return f"Event({self.event_type}, {self.data})"


class EventEmitter:
    """
    Event emitter that observers can subscribe to.

    More flexible than Subject-Observer - observers subscribe to specific events.
    """

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}

    def on(self, event_type: str, handler: Callable):
        """Subscribe to event."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        print(f"Handler registered for {event_type}: {handler.__name__}")

    def off(self, event_type: str, handler: Callable):
        """Unsubscribe from event."""
        if event_type in self._handlers:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
                print(f"Handler unregistered from {event_type}: {handler.__name__}")

    def emit(self, event: Event):
        """Emit event to all handlers."""
        print(f"\nEmitting {event}")
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                handler(event)

    def get_listener_count(self, event_type: str) -> int:
        """Get number of listeners for event type."""
        return len(self._handlers.get(event_type, []))


# ============================================================================
# 4. UI EVENT SYSTEM
# ============================================================================

class Button:
    """
    Button with click event observers.

    Demonstrates event-driven UI pattern.
    """

    def __init__(self, name: str):
        self.name = name
        self.click_handlers: List[Callable] = []
        self.hover_handlers: List[Callable] = []
        self.click_count = 0

    def on_click(self, handler: Callable):
        """Register click handler."""
        self.click_handlers.append(handler)

    def on_hover(self, handler: Callable):
        """Register hover handler."""
        self.hover_handlers.append(handler)

    def click(self):
        """Simulate button click."""
        self.click_count += 1
        print(f"\nButton '{self.name}' clicked (count: {self.click_count})")
        for handler in self.click_handlers:
            handler(self)

    def hover(self):
        """Simulate button hover."""
        print(f"\nButton '{self.name}' hovered")
        for handler in self.hover_handlers:
            handler(self)


class Form:
    """
    Form with multiple buttons.

    Demonstrates multiple buttons with different behaviors.
    """

    def __init__(self, name: str):
        self.name = name
        self.submit_button = Button("Submit")
        self.cancel_button = Button("Cancel")
        self.reset_button = Button("Reset")
        self.data = {}

    def setup_handlers(self):
        """Setup button handlers."""
        self.submit_button.on_click(self._on_submit)
        self.cancel_button.on_click(self._on_cancel)
        self.reset_button.on_click(self._on_reset)

    def _on_submit(self, button: Button):
        """Handle submit."""
        print(f"  Form {self.name} submitted with data: {self.data}")

    def _on_cancel(self, button: Button):
        """Handle cancel."""
        print(f"  Form {self.name} cancelled")

    def _on_reset(self, button: Button):
        """Handle reset."""
        self.data = {}
        print(f"  Form {self.name} reset")


# ============================================================================
# 5. NOTIFICATION SYSTEM WITH PRIORITIES
# ============================================================================

class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


class Notification:
    """Represents a notification."""

    def __init__(self, message: str, priority: NotificationPriority = NotificationPriority.MEDIUM):
        self.message = message
        self.priority = priority
        self.timestamp = datetime.now()

    def __str__(self):
        return f"[{self.priority.name}] {self.message}"


class NotificationService:
    """
    Service that sends notifications with observers handling delivery.
    """

    def __init__(self):
        self.observers: List["NotificationObserver"] = []
        self.notification_history: List[Notification] = []

    def subscribe(self, observer: "NotificationObserver"):
        """Subscribe to notifications."""
        if observer not in self.observers:
            self.observers.append(observer)
            print(f"{observer.__class__.__name__} subscribed to notifications")

    def unsubscribe(self, observer: "NotificationObserver"):
        """Unsubscribe from notifications."""
        if observer in self.observers:
            self.observers.remove(observer)

    def notify(self, notification: Notification):
        """Send notification to all observers."""
        self.notification_history.append(notification)

        # Sort observers by priority (those handling HIGH might come first)
        for observer in sorted(self.observers, key=lambda o: o.priority.value, reverse=True):
            observer.on_notification(notification)


class NotificationObserver(ABC):
    """Abstract observer for notifications."""

    def __init__(self, priority: NotificationPriority = NotificationPriority.MEDIUM):
        self.priority = priority

    @abstractmethod
    def on_notification(self, notification: Notification):
        """Handle notification."""
        pass


class EmailNotifier(NotificationObserver):
    """Send notifications via email."""

    def on_notification(self, notification: Notification):
        """Send email notification."""
        print(f"  EMAIL: Sending notification: {notification}")


class SMSNotifier(NotificationObserver):
    """Send notifications via SMS."""

    def on_notification(self, notification: Notification):
        """Send SMS notification."""
        if notification.priority.value >= NotificationPriority.HIGH.value:
            print(f"  SMS: Sending HIGH/CRITICAL notification: {notification}")


class LogNotifier(NotificationObserver):
    """Log notifications."""

    def on_notification(self, notification: Notification):
        """Log notification."""
        print(f"  LOG: {notification}")


# ============================================================================
# DEMONSTRATION AND TESTING
# ============================================================================

def test_simple_observer():
    """Test simple observer pattern."""
    print("\n" + "="*70)
    print("TEST 1: SIMPLE OBSERVER PATTERN")
    print("="*70)

    class ConcreteObserver(Observer):
        def __init__(self, name: str):
            self.name = name

        def update(self, subject: Subject):
            print(f"  {self.name} received notification. State: {subject.state}")

    subject = Subject()
    observer1 = ConcreteObserver("Observer1")
    observer2 = ConcreteObserver("Observer2")

    subject.attach(observer1)
    subject.attach(observer2)

    print("\nChanging subject state:")
    subject.state = "NEW STATE"

    print("\nDetaching observer1:")
    subject.detach(observer1)

    print("\nChanging state again:")
    subject.state = "ANOTHER STATE"


def test_stock_market():
    """Test stock market observer example."""
    print("\n" + "="*70)
    print("TEST 2: STOCK MARKET OBSERVER")
    print("="*70)

    # Create stocks
    apple = Stock("AAPL", 150.0)
    google = Stock("GOOGL", 2800.0)

    # Create traders and analysts
    trader1 = StockTrader("Alice", 145.0)
    trader2 = StockTrader("Bob", 2700.0)
    analyst = StockAnalyst("Charlie")

    # Attach observers
    apple.attach_observer(trader1)
    apple.attach_observer(analyst)
    google.attach_observer(trader2)
    google.attach_observer(analyst)

    # Simulate price changes
    apple.update_price(148.0)
    apple.update_price(144.0)  # Below trader1's target
    apple.update_price(144.5)

    google.update_price(2750.0)
    google.update_price(2680.0)  # Below trader2's target


def test_event_emitter():
    """Test event-based observer system."""
    print("\n" + "="*70)
    print("TEST 3: EVENT-BASED OBSERVER SYSTEM")
    print("="*70)

    emitter = EventEmitter()

    # Define handlers
    def on_user_login(event: Event):
        print(f"  User {event.data['username']} logged in")

    def on_user_logout(event: Event):
        print(f"  User {event.data['username']} logged out")

    def on_error(event: Event):
        print(f"  ERROR: {event.data['message']}")

    # Subscribe to events
    emitter.on("user_login", on_user_login)
    emitter.on("user_logout", on_user_logout)
    emitter.on("error", on_error)
    emitter.on("user_login", lambda e: print(f"    [Log] Login from {e.data['ip']}"))

    # Emit events
    emitter.emit(Event("user_login", {"username": "alice", "ip": "192.168.1.1"}))
    emitter.emit(Event("user_logout", {"username": "alice"}))
    emitter.emit(Event("error", {"message": "Connection failed"}))

    print(f"\nListeners for 'user_login': {emitter.get_listener_count('user_login')}")


def test_ui_events():
    """Test UI event system."""
    print("\n" + "="*70)
    print("TEST 4: UI EVENT SYSTEM")
    print("="*70)

    form = Form("LoginForm")
    form.setup_handlers()

    # Simulate form interactions
    form.submit_button.click()
    form.data = {"username": "alice", "password": "secret"}
    form.submit_button.click()

    form.reset_button.click()


def test_notification_system():
    """Test notification system with priorities."""
    print("\n" + "="*70)
    print("TEST 5: NOTIFICATION SYSTEM WITH PRIORITIES")
    print("="*70)

    service = NotificationService()

    # Create notifiers
    email = EmailNotifier(NotificationPriority.MEDIUM)
    sms = SMSNotifier(NotificationPriority.HIGH)
    log = LogNotifier(NotificationPriority.LOW)

    # Subscribe
    service.subscribe(email)
    service.subscribe(sms)
    service.subscribe(log)

    # Send notifications
    print("\nSending notifications:")
    service.notify(Notification("Welcome to the app", NotificationPriority.LOW))
    service.notify(Notification("Your balance is low", NotificationPriority.MEDIUM))
    service.notify(Notification("Unauthorized access attempt", NotificationPriority.CRITICAL))


def test_observer_memory_management():
    """Test proper observer cleanup to prevent memory leaks."""
    print("\n" + "="*70)
    print("TEST 6: OBSERVER MEMORY MANAGEMENT")
    print("="*70)

    subject = Subject()

    class TemporaryObserver(Observer):
        def update(self, subject: Subject):
            print(f"  TemporaryObserver received: {subject.state}")

    observer = TemporaryObserver()
    subject.attach(observer)

    print("State change with observer attached:")
    subject.state = "STATE 1"

    print("\nAfter detaching observer:")
    subject.detach(observer)
    subject.state = "STATE 2"

    print("\nNo observer received the second state change!")


def test_multiple_observers():
    """Test multiple observers of same type."""
    print("\n" + "="*70)
    print("TEST 7: MULTIPLE OBSERVERS")
    print("="*70)

    class CounterObserver(Observer):
        counter = 0

        def __init__(self):
            CounterObserver.counter += 1
            self.id = CounterObserver.counter
            self.update_count = 0

        def update(self, subject: Subject):
            self.update_count += 1
            print(f"  Observer {self.id} updated (count: {self.update_count})")

    subject = Subject()
    observers = [CounterObserver() for _ in range(5)]

    for observer in observers:
        subject.attach(observer)

    print(f"\nAttached {len(observers)} observers")
    subject.state = "NEW STATE"

    print(f"All observers received update: {all(o.update_count == 1 for o in observers)}")


# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

def print_key_takeaways():
    """Print key learning points."""
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. LOOSE COUPLING
   - Subject doesn't know details of observers
   - Observers don't depend on each other
   - Easy to add/remove observers at runtime
   - Perfect for event-driven systems

2. PUSH VS PULL MODELS
   Push Model:
   - Subject sends data to observers
   - Observers receive complete information
   - More efficient if observers need same data

   Pull Model:
   - Subject notifies observers
   - Observers request data from subject
   - Better if observers need different subsets of data

3. MEMORY LEAK PREVENTION
   CRITICAL: Always unsubscribe observers!
   - Unregistered observers won't be garbage collected
   - Keep references in subject longer than needed
   - Solution: Explicitly detach/unsubscribe observers
   - Or: Use weak references (advanced)

4. ORDER OF NOTIFICATION
   - Notification order may be unpredictable
   - Don't assume specific order
   - If order matters, use explicit ordering
   - Or use priority-based notification

5. EVENT-BASED SYSTEMS
   - More flexible than simple Observer
   - Observers subscribe to specific event types
   - Easy to add new event types
   - Callbacks/function handlers more common

6. UI EVENT SYSTEMS
   - Buttons, forms, inputs generate events
   - Handlers react to user interactions
   - Multiple handlers per event possible
   - Foundation of modern UI frameworks

7. REAL-WORLD APPLICATIONS
   - Stock market tickers (traders watching stocks)
   - UI event handling (button clicks, form submissions)
   - Publish-Subscribe systems (message brokers)
   - Change notifications (model updates in MVC)
   - Event streams (user activity, log events)
   - Reactive systems (reactive programming)

8. WHEN TO USE OBSERVER
   - One-to-many dependencies needed
   - Changes in one object should update others
   - Event-driven architecture
   - Loose coupling required
   - Dynamic subscription/unsubscription

9. ANTI-PATTERNS TO AVOID
   - Not unsubscribing observers (memory leaks!)
   - Assuming notification order
   - Creating circular observer dependencies
   - Modifying observer list during notification
   - Synchronous heavy processing in observers

10. MODERN ALTERNATIVES
    - Reactive frameworks (RxPython, RxJavaScript)
    - Event emitters (Node.js EventEmitter)
    - Message brokers (RabbitMQ, Kafka)
    - Pub-Sub services (Google Pub/Sub, AWS SNS)
    - But Observer pattern is the foundation for all of them
    """)


if __name__ == "__main__":
    test_simple_observer()
    test_stock_market()
    test_event_emitter()
    test_ui_events()
    test_notification_system()
    test_observer_memory_management()
    test_multiple_observers()
    print_key_takeaways()
