"""
Support Ticket Routing using Chain of Responsibility
"""

from abc import ABC, abstractmethod
from typing import Optional


class SupportTicket:
    """Support ticket to be processed."""
    
    def __init__(self, ticket_id: str, issue: str, priority: int):
        self.ticket_id = ticket_id
        self.issue = issue
        self.priority = priority  # 1=low, 2=medium, 3=high
        self.assigned_to = None
    
    def __str__(self):
        return f"Ticket({self.ticket_id}, priority={self.priority}, {self.issue})"


class SupportHandler(ABC):
    """Abstract handler in the chain."""
    
    def __init__(self, name: str, max_priority: int):
        self.name = name
        self.max_priority = max_priority
        self.next_handler: Optional[SupportHandler] = None
    
    def set_next(self, handler: "SupportHandler") -> "SupportHandler":
        """Set next handler in chain."""
        self.next_handler = handler
        return handler  # Enables chaining
    
    def handle(self, ticket: SupportTicket):
        """Handle ticket or pass to next handler."""
        if ticket.priority <= self.max_priority:
            self.process(ticket)
        elif self.next_handler:
            print(f"{self.name}: Can't handle, passing to {self.next_handler.name}")
            self.next_handler.handle(ticket)
        else:
            print(f"ERROR: No handler for {ticket}")
    
    @abstractmethod
    def process(self, ticket: SupportTicket):
        """Process the ticket."""
        pass


class BasicSupport(SupportHandler):
    """Handles low priority tickets (1)."""
    
    def process(self, ticket: SupportTicket):
        """Process basic ticket."""
        print(f"{self.name}: Handling {ticket}")
        ticket.assigned_to = self.name
        print(f"  Resolved: {ticket.issue}")


class TechnicalSupport(SupportHandler):
    """Handles medium priority tickets (2)."""
    
    def process(self, ticket: SupportTicket):
        """Process technical ticket."""
        print(f"{self.name}: Handling {ticket}")
        ticket.assigned_to = self.name
        print(f"  Investigating technical issue: {ticket.issue}")


class ManagerSupport(SupportHandler):
    """Handles high priority tickets (3)."""
    
    def process(self, ticket: SupportTicket):
        """Process critical ticket."""
        print(f"{self.name}: Handling {ticket}")
        ticket.assigned_to = self.name
        print(f"  Escalating to management: {ticket.issue}")


def demonstrate():
    """Demonstrate chain of responsibility."""
    print("="*70)
    print("SUPPORT TICKET ROUTING")
    print("="*70)
    
    # Create handler chain
    basic = BasicSupport("Basic Support", 1)
    technical = TechnicalSupport("Technical Support", 2)
    manager = ManagerSupport("Manager", 3)
    
    # Link handlers
    basic.set_next(technical).set_next(manager)
    
    # Process tickets
    print("\n1. Low priority ticket:")
    basic.handle(SupportTicket("T001", "Password reset", 1))
    
    print("\n2. Medium priority ticket:")
    basic.handle(SupportTicket("T002", "Software crash", 2))
    
    print("\n3. High priority ticket:")
    basic.handle(SupportTicket("T003", "System down", 3))


if __name__ == "__main__":
    demonstrate()
    print("\n" + "="*70)
    print("KEY POINTS")
    print("="*70)
    print("""
1. Request passes through chain until handled
2. Each handler decides: process or pass along
3. Order matters (basic -> technical -> manager)
4. Can add/remove handlers dynamically
5. Decouples sender from receiver
    """)
