# Observer Pattern

## The Hook: The Newsletter Problem

How does a news website notify thousands of subscribers when a new article is published? The website (subject) doesn't want to know about each subscriber's email client, notification preferences, or delivery method. Subscribers (observers) just want updates without polling constantly.

This is the Observer pattern: define a one-to-many dependency where changing one object automatically notifies all dependent objects.

## The Problem: Keeping State Synchronized

When one object's state changes, many other objects need to know:
- Stock price changes notify traders, analysts, and display screens
- Model changes update multiple views (MVC pattern)
- Button clicks trigger multiple event handlers
- System events notify multiple subscribers

**Without Observer:**
- Tight coupling between subject and dependents
- Subject must know all dependents explicitly
- Hard to add/remove dependents dynamically
- Dependents must poll for changes (inefficient)

## The Solution: Publish-Subscribe Mechanism

Observer decouples subjects from observers through a subscription mechanism.

**Key Components:**
- Subject: Maintains list of observers, notifies them of changes
- Observer: Interface with update() method
- Concrete Observers: Implement update() to respond to changes

**How It Works:**
1. Observers register with subject
2. Subject's state changes
3. Subject notifies all registered observers
4. Each observer responds independently

**Models:**
- Push: Subject sends changed data to observers
- Pull: Observers request data from subject when notified

## When to Use

Use Observer when:
- One-to-many dependencies between objects
- Object changes should trigger updates in others
- Don't know how many dependents at compile time
- Want loose coupling between subject and observers
- Event-driven architectures

**Common Applications:**
- UI event systems (button clicks, form changes)
- Model-View architectures
- Publish-subscribe messaging
- Real-time data feeds
- Notification systems

## Trade-offs

**Gains:**
- Loose coupling between subject and observers
- Dynamic subscription/unsubscription
- Broadcast communication
- Open/Closed principle (add observers without modifying subject)

**Losses:**
- Unpredictable notification order
- Memory leaks if observers not unregistered
- Performance cost with many observers
- Difficult debugging (who changed what?)
- Unexpected update chains

## The Verdict

Observer is foundational for event-driven systems and MVC architectures. It enables loose coupling and dynamic relationships. But beware memory leaks from unregistered observers and the debugging complexity of cascading updates. Always unsubscribe observers when done.
