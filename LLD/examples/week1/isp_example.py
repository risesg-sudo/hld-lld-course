"""
SOLID PRINCIPLE #4: INTERFACE SEGREGATION PRINCIPLE (ISP)
===========================================================

Core Concept:
Clients should not be forced to depend on interfaces they do not use.
It's better to have many specific interfaces than one general-purpose interface.
Break large interfaces into smaller, more specific ones.

Benefits:
- Classes are not forced to implement methods they don't need
- Interfaces are more focused and cohesive
- Easier to implement and maintain
- Reduces coupling between classes
- Makes code more flexible and extensible

Real-world analogy:
Instead of hiring someone who must be a chef, janitor, and driver,
hire separate people for each role. Each person has a focused job.
"""

from abc import ABC, abstractmethod
from typing import List


# ============================================================================
# BAD EXAMPLE: Fat Interface - Forcing Implementation of Unused Methods
# ============================================================================

class BadMultiFunctionDevice(ABC):
    """
    This interface is too fat - it forces all implementations to provide
    methods they might not need.

    A simple printer shouldn't have to implement scan() or fax() methods.
    A copier that can't print shouldn't have to implement print() method.
    """

    @abstractmethod
    def print(self, document: str) -> bool:
        """Print a document."""
        pass

    @abstractmethod
    def scan(self, document_path: str) -> str:
        """Scan a document."""
        pass

    @abstractmethod
    def fax(self, document: str, number: str) -> bool:
        """Send a fax."""
        pass

    @abstractmethod
    def copy(self, document: str) -> str:
        """Copy a document."""
        pass


class BadSimplePrinter(BadMultiFunctionDevice):
    """
    A simple printer that only prints.
    But it's forced to implement scan(), fax(), and copy() - methods it doesn't have!
    """

    def print(self, document: str) -> bool:
        print(f"✓ Printing: {document}")
        return True

    def scan(self, document_path: str) -> str:
        """This printer cannot scan!"""
        raise NotImplementedError("This printer cannot scan")

    def fax(self, document: str, number: str) -> bool:
        """This printer cannot fax!"""
        raise NotImplementedError("This printer cannot fax")

    def copy(self, document: str) -> str:
        """This printer cannot copy!"""
        raise NotImplementedError("This printer cannot copy")


class BadCopier(BadMultiFunctionDevice):
    """
    A copier that only copies.
    But it's forced to implement print(), scan(), and fax() - methods it doesn't have!
    """

    def print(self, document: str) -> bool:
        """This copier cannot print!"""
        raise NotImplementedError("This copier cannot print")

    def scan(self, document_path: str) -> str:
        """This copier cannot scan!"""
        raise NotImplementedError("This copier cannot scan")

    def fax(self, document: str, number: str) -> bool:
        """This copier cannot fax!"""
        raise NotImplementedError("This copier cannot fax")

    def copy(self, document: str) -> str:
        print(f"✓ Copying: {document}")
        return f"Copy of {document}"


def demo_bad_isp():
    """Demonstrate ISP violation."""
    print("\n" + "="*70)
    print("BAD EXAMPLE: ISP Violation - Fat Interface")
    print("="*70)

    print("\n1. Using simple printer:")
    printer = BadSimplePrinter()
    printer.print("Document.pdf")

    print("\n2. Trying operations that don't exist:")
    try:
        printer.scan("Document.pdf")
    except NotImplementedError as e:
        print(f"✗ Error: {e}")

    try:
        printer.fax("Document.pdf", "555-1234")
    except NotImplementedError as e:
        print(f"✗ Error: {e}")

    print("\n3. Using copier:")
    copier = BadCopier()
    copier.copy("Document.pdf")

    print("\n4. Trying operations that don't exist:")
    try:
        copier.print("Document.pdf")
    except NotImplementedError as e:
        print(f"✗ Error: {e}")

    print("\nProblems:")
    print("  - Classes forced to implement methods they don't have")
    print("  - Raises NotImplementedError - violates Liskov Substitution")
    print("  - Fat interface couples clients to unnecessary methods")
    print("  - Hard to understand what each device actually does")


# ============================================================================
# GOOD EXAMPLE: Segregated Interfaces - Specific Interfaces
# ============================================================================

class Printer(ABC):
    """Interface for printing functionality."""

    @abstractmethod
    def print(self, document: str) -> bool:
        """Print a document."""
        pass


class Scanner(ABC):
    """Interface for scanning functionality."""

    @abstractmethod
    def scan(self, document_path: str) -> str:
        """Scan a document."""
        pass


class FaxMachine(ABC):
    """Interface for faxing functionality."""

    @abstractmethod
    def fax(self, document: str, number: str) -> bool:
        """Send a fax."""
        pass


class Copier(ABC):
    """Interface for copying functionality."""

    @abstractmethod
    def copy(self, document: str) -> str:
        """Copy a document."""
        pass


class SimplePrinter(Printer):
    """
    A simple printer that only prints.
    Now it only implements the Printer interface - clean and focused!
    """

    def print(self, document: str) -> bool:
        print(f"✓ Printing: {document}")
        return True


class MultiPurposeDevice(Printer, Scanner, FaxMachine, Copier):
    """
    A multi-function device that can do everything.
    It implements only the interfaces it actually supports.
    """

    def print(self, document: str) -> bool:
        print(f"✓ Printing: {document}")
        return True

    def scan(self, document_path: str) -> str:
        print(f"✓ Scanning: {document_path}")
        return f"Scanned version of {document_path}"

    def fax(self, document: str, number: str) -> bool:
        print(f"✓ Faxing '{document}' to {number}")
        return True

    def copy(self, document: str) -> str:
        print(f"✓ Copying: {document}")
        return f"Copy of {document}"


class BasicCopier(Copier):
    """
    A copier that only copies.
    It only implements the Copier interface - no unnecessary methods!
    """

    def copy(self, document: str) -> str:
        print(f"✓ Copying: {document}")
        return f"Copy of {document}"


class ScannerDevice(Scanner):
    """
    A standalone scanner.
    It only implements the Scanner interface.
    """

    def scan(self, document_path: str) -> str:
        print(f"✓ Scanning: {document_path}")
        return f"Scanned version of {document_path}"


def demo_good_isp():
    """Demonstrate proper ISP implementation."""
    print("\n" + "="*70)
    print("GOOD EXAMPLE: Following ISP - Segregated Interfaces")
    print("="*70)

    print("\n1. Simple printer (implements only Printer):")
    printer = SimplePrinter()
    printer.print("Document.pdf")

    print("\n2. Multi-purpose device (implements all interfaces):")
    mfd = MultiPurposeDevice()
    mfd.print("Report.pdf")
    mfd.scan("Form.pdf")
    mfd.copy("Letter.pdf")
    mfd.fax("Invoice.pdf", "555-1234")

    print("\n3. Basic copier (implements only Copier):")
    copier = BasicCopier()
    copier.copy("Document.pdf")

    print("\n4. Scanner device (implements only Scanner):")
    scanner = ScannerDevice()
    scanner.scan("Photo.jpg")

    print("\nBenefits:")
    print("  ✓ Each class implements only what it needs")
    print("  ✓ No NotImplementedError exceptions")
    print("  ✓ Clear what each device can do")
    print("  ✓ Easy to add new devices with different capabilities")
    print("  ✓ No unused method implementations")


# ============================================================================
# REAL-WORLD EXAMPLE: Database Operations
# ============================================================================

class Readable(ABC):
    """Interface for read operations."""

    @abstractmethod
    def read(self, query: str) -> List[dict]:
        """Execute a read query."""
        pass


class Writable(ABC):
    """Interface for write operations."""

    @abstractmethod
    def write(self, table: str, data: dict) -> bool:
        """Write data to database."""
        pass


class Updatable(ABC):
    """Interface for update operations."""

    @abstractmethod
    def update(self, table: str, id: int, data: dict) -> bool:
        """Update existing record."""
        pass


class Deletable(ABC):
    """Interface for delete operations."""

    @abstractmethod
    def delete(self, table: str, id: int) -> bool:
        """Delete a record."""
        pass


class ReadOnlyDatabase(Readable):
    """
    Read-only database connection.
    Implements only the Readable interface.
    """

    def read(self, query: str) -> List[dict]:
        print(f"✓ Executing read query: {query}")
        return [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]


class FullAccessDatabase(Readable, Writable, Updatable, Deletable):
    """
    Database with full CRUD access.
    Implements all necessary interfaces.
    """

    def read(self, query: str) -> List[dict]:
        print(f"✓ Reading: {query}")
        return []

    def write(self, table: str, data: dict) -> bool:
        print(f"✓ Writing to {table}: {data}")
        return True

    def update(self, table: str, id: int, data: dict) -> bool:
        print(f"✓ Updating {table} ID {id}: {data}")
        return True

    def delete(self, table: str, id: int) -> bool:
        print(f"✓ Deleting from {table} ID {id}")
        return True


class WriteOnlyLogger(Writable):
    """
    Write-only database for logging.
    Implements only the Writable interface.
    """

    def write(self, table: str, data: dict) -> bool:
        print(f"✓ Logging to {table}: {data}")
        return True


def demo_real_world():
    """Demonstrate real-world ISP usage."""
    print("\n" + "="*70)
    print("REAL-WORLD EXAMPLE: Database Operations with ISP")
    print("="*70)

    print("\n1. Read-only database (only implements Readable):")
    read_db = ReadOnlyDatabase()
    read_db.read("SELECT * FROM users")

    print("\n2. Full-access database (implements all interfaces):")
    full_db = FullAccessDatabase()
    full_db.read("SELECT * FROM users")
    full_db.write("logs", {"event": "user_login"})
    full_db.update("users", 1, {"name": "John Updated"})
    full_db.delete("users", 2)

    print("\n3. Write-only logger (only implements Writable):")
    logger = WriteOnlyLogger()
    logger.write("audit_log", {"action": "file_created", "user": "admin"})

    print("\nBenefit: Each database has only the operations it needs.")
    print("No unnecessary or impossible operations.")


# ============================================================================
# REAL-WORLD EXAMPLE #2: User Roles and Permissions
# ============================================================================

class CanViewReports(ABC):
    """Permission to view reports."""

    @abstractmethod
    def view_reports(self) -> List[str]:
        """View available reports."""
        pass


class CanCreateReports(ABC):
    """Permission to create reports."""

    @abstractmethod
    def create_report(self, name: str) -> bool:
        """Create a new report."""
        pass


class CanDeleteReports(ABC):
    """Permission to delete reports."""

    @abstractmethod
    def delete_report(self, report_id: int) -> bool:
        """Delete a report."""
        pass


class CanManageUsers(ABC):
    """Permission to manage users."""

    @abstractmethod
    def add_user(self, name: str) -> bool:
        """Add a new user."""
        pass


class Viewer(CanViewReports):
    """User role that can only view reports."""

    def view_reports(self) -> List[str]:
        print("✓ Viewing reports")
        return ["Sales Report", "Inventory Report"]


class Editor(CanViewReports, CanCreateReports, CanDeleteReports):
    """User role that can view, create, and delete reports."""

    def view_reports(self) -> List[str]:
        return ["Sales Report", "Inventory Report"]

    def create_report(self, name: str) -> bool:
        print(f"✓ Creating report: {name}")
        return True

    def delete_report(self, report_id: int) -> bool:
        print(f"✓ Deleting report {report_id}")
        return True


class Admin(CanViewReports, CanCreateReports, CanDeleteReports, CanManageUsers):
    """Admin role with all permissions."""

    def view_reports(self) -> List[str]:
        return ["Sales Report", "Inventory Report"]

    def create_report(self, name: str) -> bool:
        print(f"✓ Creating report: {name}")
        return True

    def delete_report(self, report_id: int) -> bool:
        print(f"✓ Deleting report {report_id}")
        return True

    def add_user(self, name: str) -> bool:
        print(f"✓ Adding user: {name}")
        return True


def demo_user_roles():
    """Demonstrate user roles with ISP."""
    print("\n" + "="*70)
    print("REAL-WORLD EXAMPLE #2: User Roles with ISP")
    print("="*70)

    print("\n1. Viewer role (only view):")
    viewer = Viewer()
    viewer.view_reports()

    print("\n2. Editor role (view, create, delete):")
    editor = Editor()
    editor.view_reports()
    editor.create_report("Monthly Report")
    editor.delete_report(1)

    print("\n3. Admin role (all permissions):")
    admin = Admin()
    admin.view_reports()
    admin.create_report("System Report")
    admin.delete_report(2)
    admin.add_user("new_user")

    print("\nBenefit: Each role has only the permissions it needs.")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("INTERFACE SEGREGATION PRINCIPLE (ISP) EXAMPLES")
    print("="*70)

    # Bad example
    demo_bad_isp()

    # Good example
    demo_good_isp()

    # Real-world example 1
    demo_real_world()

    # Real-world example 2
    demo_user_roles()

    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. Don't force clients to depend on interfaces they don't use
2. Break large interfaces into smaller, specific ones
3. Each interface should have a single purpose
4. A class should implement only the interfaces it actually needs
5. Use multiple inheritance to combine specific interfaces
6. This reduces coupling and increases flexibility
7. Makes code easier to maintain and extend
8. Clients depend only on what they actually use
9. Related to Single Responsibility Principle
    """)
