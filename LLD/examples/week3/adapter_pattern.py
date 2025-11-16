"""
Adapter Pattern - Convert interface of a class into another clients expect.

This module demonstrates various adapter implementations:
1. Legacy system integration (old interface to new)
2. API adapters (third-party to internal interface)
3. Database adapters (multiple database support)
4. Format conversion (JSON to XML, XML to CSV)
5. Hardware interface adapters (different device types)
6. Two-way adapters (bidirectional conversion)

Key Learning Points:
- Adapter allows incompatible interfaces to work together
- Can adapt legacy code, third-party libraries, external APIs
- Object adapter uses composition (more flexible)
- Class adapter uses inheritance (less flexible, not always possible)
- Adapter is transparent to client code
- Good alternative to modifying existing code
"""

from abc import ABC, abstractmethod
from typing import Any, List, Dict
import json
import xml.etree.ElementTree as ET
from datetime import datetime


# ============================================================================
# 1. LEGACY SYSTEM INTEGRATION ADAPTER
# ============================================================================

class ModernPaymentProcessor:
    """Modern payment processor interface."""

    def process_payment(self, amount: float, method: str) -> bool:
        """Process payment with modern interface."""
        print(f"Processing payment: ${amount:.2f} via {method}")
        return True


class LegacyPaymentSystem:
    """Legacy payment system with old interface."""

    def make_payment(self, sum_amount, payment_mode):
        """Old interface - different naming and parameters."""
        print(f"Legacy system: Processing ${sum_amount} with mode={payment_mode}")
        return True


class LegacyPaymentAdapter(ModernPaymentProcessor):
    """
    Adapter to use legacy payment system with modern interface.

    This adapter converts modern interface calls to legacy interface calls.
    """

    def __init__(self, legacy_system: LegacyPaymentSystem):
        self.legacy_system = legacy_system

    def process_payment(self, amount: float, method: str) -> bool:
        """Adapt modern interface to legacy interface."""
        # Convert modern interface to legacy interface
        return self.legacy_system.make_payment(amount, method)


# ============================================================================
# 2. DATABASE ADAPTER EXAMPLE
# ============================================================================

class DatabaseInterface(ABC):
    """Standard database interface."""

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def query(self, sql: str) -> List[Dict]:
        pass

    @abstractmethod
    def insert(self, table: str, data: Dict) -> bool:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


class MySQLDatabase(DatabaseInterface):
    """Native MySQL implementation."""

    def connect(self) -> bool:
        print("MySQL: Connected")
        return True

    def query(self, sql: str) -> List[Dict]:
        print(f"MySQL: Executing query: {sql[:50]}...")
        return [{"id": 1, "name": "John"}]

    def insert(self, table: str, data: Dict) -> bool:
        print(f"MySQL: Inserting into {table}: {data}")
        return True

    def close(self) -> None:
        print("MySQL: Connection closed")


class PostgreSQLDatabase(DatabaseInterface):
    """Native PostgreSQL implementation."""

    def connect(self) -> bool:
        print("PostgreSQL: Connected")
        return True

    def query(self, sql: str) -> List[Dict]:
        print(f"PostgreSQL: Executing query: {sql[:50]}...")
        return [{"id": 1, "name": "John"}]

    def insert(self, table: str, data: Dict) -> bool:
        print(f"PostgreSQL: Inserting into {table}: {data}")
        return True

    def close(self) -> None:
        print("PostgreSQL: Connection closed")


class MongoDBLegacyAPI:
    """
    Legacy MongoDB API with different interface.

    This simulates a third-party library with non-standard interface.
    """

    def open_connection(self, connection_string: str) -> None:
        print(f"MongoDB: Opening connection")

    def find_document(self, collection: str, filter: Dict) -> List[Dict]:
        print(f"MongoDB: Finding in collection '{collection}'")
        return [{"_id": "1", "name": "John"}]

    def insert_document(self, collection: str, doc: Dict) -> None:
        print(f"MongoDB: Inserting into '{collection}'")

    def disconnect(self) -> None:
        print("MongoDB: Disconnection")


class MongoDBAdapter(DatabaseInterface):
    """Adapter to use MongoDB with standard database interface."""

    def __init__(self, legacy_mongo: MongoDBLegacyAPI):
        self.mongo = legacy_mongo

    def connect(self) -> bool:
        self.mongo.open_connection("mongodb://localhost")
        return True

    def query(self, sql: str) -> List[Dict]:
        # Convert SQL to MongoDB find
        collection = "users"  # Extracted from SQL
        return self.mongo.find_document(collection, {})

    def insert(self, table: str, data: Dict) -> bool:
        self.mongo.insert_document(table, data)
        return True

    def close(self) -> None:
        self.mongo.disconnect()


# ============================================================================
# 3. API ADAPTER EXAMPLE
# ============================================================================

class PaymentGatewayInterface(ABC):
    """Standard payment gateway interface."""

    @abstractmethod
    def authorize(self, amount: float, card: str) -> bool:
        pass

    @abstractmethod
    def capture(self, transaction_id: str) -> bool:
        pass

    @abstractmethod
    def refund(self, transaction_id: str) -> bool:
        pass


class StripePaymentGateway(PaymentGatewayInterface):
    """Native Stripe gateway implementation."""

    def authorize(self, amount: float, card: str) -> bool:
        print(f"Stripe: Authorizing ${amount}")
        return True

    def capture(self, transaction_id: str) -> bool:
        print(f"Stripe: Capturing transaction {transaction_id}")
        return True

    def refund(self, transaction_id: str) -> bool:
        print(f"Stripe: Refunding transaction {transaction_id}")
        return True


class PayPalLegacyAPI:
    """
    Legacy PayPal API with different naming conventions.

    Simulates third-party API with its own interface.
    """

    def request_auth(self, value: float, payment_info: str) -> str:
        print(f"PayPal: Requesting authorization for ${value}")
        return "PAYPAL_AUTH_123"

    def execute_payment(self, auth_id: str) -> bool:
        print(f"PayPal: Executing payment for auth {auth_id}")
        return True

    def make_refund(self, auth_id: str) -> bool:
        print(f"PayPal: Making refund for auth {auth_id}")
        return True


class PayPalAdapter(PaymentGatewayInterface):
    """Adapter for PayPal legacy API."""

    def __init__(self, paypal_api: PayPalLegacyAPI):
        self.paypal = paypal_api
        self.auth_id = None

    def authorize(self, amount: float, card: str) -> bool:
        self.auth_id = self.paypal.request_auth(amount, card)
        return True

    def capture(self, transaction_id: str) -> bool:
        return self.paypal.execute_payment(self.auth_id)

    def refund(self, transaction_id: str) -> bool:
        return self.paypal.make_refund(self.auth_id)


# ============================================================================
# 4. DATA FORMAT CONVERTER ADAPTER
# ============================================================================

class DataFormat(ABC):
    """Standard data format interface."""

    @abstractmethod
    def serialize(self, data: Dict) -> str:
        pass

    @abstractmethod
    def deserialize(self, content: str) -> Dict:
        pass


class JSONFormat(DataFormat):
    """Native JSON format."""

    def serialize(self, data: Dict) -> str:
        return json.dumps(data)

    def deserialize(self, content: str) -> Dict:
        return json.loads(content)


class XMLLegacyAPI:
    """Legacy XML API with different interface."""

    def convert_dict_to_xml(self, dictionary: Dict) -> str:
        root = ET.Element("data")
        for key, value in dictionary.items():
            child = ET.SubElement(root, key)
            child.text = str(value)
        return ET.tostring(root, encoding='unicode')

    def convert_xml_to_dict(self, xml_string: str) -> Dict:
        root = ET.fromstring(xml_string)
        return {child.tag: child.text for child in root}


class XMLAdapter(DataFormat):
    """Adapter for legacy XML API."""

    def __init__(self, xml_api: XMLLegacyAPI):
        self.xml_api = xml_api

    def serialize(self, data: Dict) -> str:
        return self.xml_api.convert_dict_to_xml(data)

    def deserialize(self, content: str) -> Dict:
        return self.xml_api.convert_xml_to_dict(content)


class CSVLegacyAPI:
    """Legacy CSV formatter."""

    def dict_to_csv_row(self, dictionary: Dict) -> str:
        return ",".join(f"{k}:{v}" for k, v in dictionary.items())

    def csv_row_to_dict(self, csv_row: str) -> Dict:
        result = {}
        for pair in csv_row.split(","):
            key, value = pair.split(":")
            result[key] = value
        return result


class CSVAdapter(DataFormat):
    """Adapter for legacy CSV API."""

    def __init__(self, csv_api: CSVLegacyAPI):
        self.csv_api = csv_api

    def serialize(self, data: Dict) -> str:
        return self.csv_api.dict_to_csv_row(data)

    def deserialize(self, content: str) -> Dict:
        return self.csv_api.csv_row_to_dict(content)


# ============================================================================
# 5. TWO-WAY ADAPTER
# ============================================================================

class USElectrical:
    """US electrical standard (120V, flat prongs)."""

    def provide_power(self) -> str:
        return "120V AC, Flat prongs"


class EUElectrical:
    """EU electrical standard (230V, round prongs)."""

    def get_power(self) -> str:
        return "230V AC, Round prongs"


class ElectricalAdapter:
    """
    Two-way adapter for electrical standards.

    Can adapt US to EU and vice versa.
    """

    def __init__(self, us_device: USElectrical = None, eu_device: EUElectrical = None):
        self.us_device = us_device
        self.eu_device = eu_device

    def use_in_us(self) -> str:
        """Use EU device in US."""
        if self.eu_device:
            eu_power = self.eu_device.get_power()
            # Convert 230V to 120V, round to flat prongs
            return f"Adapted: {eu_power} -> 120V AC, Flat prongs"
        return None

    def use_in_eu(self) -> str:
        """Use US device in EU."""
        if self.us_device:
            us_power = self.us_device.provide_power()
            # Convert 120V to 230V, flat to round prongs
            return f"Adapted: {us_power} -> 230V AC, Round prongs"
        return None


# ============================================================================
# 6. CLOUD SERVICE ADAPTER
# ============================================================================

class StorageInterface(ABC):
    """Standard storage interface."""

    @abstractmethod
    def upload(self, filename: str, data: bytes) -> bool:
        pass

    @abstractmethod
    def download(self, filename: str) -> bytes:
        pass

    @abstractmethod
    def delete(self, filename: str) -> bool:
        pass


class AWSStorage(StorageInterface):
    """Native AWS S3 implementation."""

    def upload(self, filename: str, data: bytes) -> bool:
        print(f"AWS S3: Uploading {filename}")
        return True

    def download(self, filename: str) -> bytes:
        print(f"AWS S3: Downloading {filename}")
        return b"file_content"

    def delete(self, filename: str) -> bool:
        print(f"AWS S3: Deleting {filename}")
        return True


class GoogleCloudLegacyAPI:
    """Legacy Google Cloud API."""

    def upload_object(self, bucket: str, object_name: str, blob: bytes) -> None:
        print(f"GCS: Uploading to {bucket}/{object_name}")

    def get_object(self, bucket: str, object_name: str) -> bytes:
        print(f"GCS: Downloading from {bucket}/{object_name}")
        return b"file_content"

    def delete_object(self, bucket: str, object_name: str) -> None:
        print(f"GCS: Deleting {bucket}/{object_name}")


class GoogleCloudAdapter(StorageInterface):
    """Adapter for Google Cloud Storage."""

    def __init__(self, gcs_api: GoogleCloudLegacyAPI, bucket: str = "my-bucket"):
        self.gcs = gcs_api
        self.bucket = bucket

    def upload(self, filename: str, data: bytes) -> bool:
        self.gcs.upload_object(self.bucket, filename, data)
        return True

    def download(self, filename: str) -> bytes:
        return self.gcs.get_object(self.bucket, filename)

    def delete(self, filename: str) -> bool:
        self.gcs.delete_object(self.bucket, filename)
        return True


# ============================================================================
# 7. DEMONSTRATION
# ============================================================================

def demo_legacy_system_integration():
    """Demonstrate legacy system adapter."""
    print("\n" + "="*60)
    print("ADAPTER PATTERN - LEGACY SYSTEM INTEGRATION")
    print("="*60)

    # Legacy system
    legacy = LegacyPaymentSystem()
    legacy.make_payment(100, "credit_card")

    # Using modern interface with adapter
    print("\nUsing modern interface with adapter:")
    adapter = LegacyPaymentAdapter(legacy)
    adapter.process_payment(100, "credit_card")


def demo_database_adapters():
    """Demonstrate database adapters."""
    print("\n" + "="*60)
    print("ADAPTER PATTERN - DATABASE ADAPTERS")
    print("="*60)

    # Using MySQL
    print("\nMySQL Database:")
    mysql = MySQLDatabase()
    mysql.connect()
    mysql.query("SELECT * FROM users")
    mysql.insert("users", {"name": "Jane"})
    mysql.close()

    # Using PostgreSQL
    print("\nPostgreSQL Database:")
    postgres = PostgreSQLDatabase()
    postgres.connect()
    postgres.query("SELECT * FROM users")
    postgres.insert("users", {"name": "Jane"})
    postgres.close()

    # Using MongoDB with adapter
    print("\nMongoDB with Adapter:")
    mongo_api = MongoDBLegacyAPI()
    mongo_adapter = MongoDBAdapter(mongo_api)
    mongo_adapter.connect()
    mongo_adapter.query("SELECT * FROM users")
    mongo_adapter.insert("users", {"name": "Jane"})
    mongo_adapter.close()

    # Using unified interface
    print("\nUnified Database Interface Usage:")
    databases: List[DatabaseInterface] = [
        mysql,
        postgres,
        mongo_adapter
    ]
    for db in databases:
        db.connect()
        results = db.query("SELECT * FROM users")
        print(f"  Results: {results}")
        db.close()


def demo_payment_gateway_adapters():
    """Demonstrate payment gateway adapters."""
    print("\n" + "="*60)
    print("ADAPTER PATTERN - PAYMENT GATEWAY ADAPTERS")
    print("="*60)

    # Using Stripe
    print("\nStripe Payment Gateway:")
    stripe = StripePaymentGateway()
    stripe.authorize(100, "4111111111111111")
    stripe.capture("stripe_txn_123")
    stripe.refund("stripe_txn_123")

    # Using PayPal with adapter
    print("\nPayPal with Adapter:")
    paypal_api = PayPalLegacyAPI()
    paypal_adapter = PayPalAdapter(paypal_api)
    paypal_adapter.authorize(100, "user@paypal.com")
    paypal_adapter.capture("paypal_txn_123")
    paypal_adapter.refund("paypal_txn_123")

    # Using unified interface
    print("\nUnified Payment Gateway Interface:")
    gateways: List[PaymentGatewayInterface] = [
        stripe,
        paypal_adapter
    ]
    for gateway in gateways:
        print(f"\nUsing {gateway.__class__.__name__}:")
        gateway.authorize(50, "card_info")


def demo_format_adapters():
    """Demonstrate format converters."""
    print("\n" + "="*60)
    print("ADAPTER PATTERN - FORMAT CONVERTERS")
    print("="*60)

    data = {"name": "John", "age": "30", "city": "NYC"}

    # JSON
    print("\nJSON Format:")
    json_fmt = JSONFormat()
    json_str = json_fmt.serialize(data)
    print(f"  Serialized: {json_str}")
    parsed = json_fmt.deserialize(json_str)
    print(f"  Deserialized: {parsed}")

    # XML with adapter
    print("\nXML Format (with Adapter):")
    xml_api = XMLLegacyAPI()
    xml_adapter = XMLAdapter(xml_api)
    xml_str = xml_adapter.serialize(data)
    print(f"  Serialized: {xml_str}")
    parsed = xml_adapter.deserialize(xml_str)
    print(f"  Deserialized: {parsed}")

    # CSV with adapter
    print("\nCSV Format (with Adapter):")
    csv_api = CSVLegacyAPI()
    csv_adapter = CSVAdapter(csv_api)
    csv_str = csv_adapter.serialize(data)
    print(f"  Serialized: {csv_str}")
    parsed = csv_adapter.deserialize(csv_str)
    print(f"  Deserialized: {parsed}")


def demo_two_way_adapter():
    """Demonstrate two-way adapter."""
    print("\n" + "="*60)
    print("ADAPTER PATTERN - TWO-WAY ADAPTER")
    print("="*60)

    us_device = USElectrical()
    eu_device = EUElectrical()

    print("\nUS Device:")
    print(f"  Provides: {us_device.provide_power()}")

    print("\nEU Device:")
    print(f"  Provides: {eu_device.get_power()}")

    print("\nUsing EU Device in US:")
    adapter_for_us = ElectricalAdapter(eu_device=eu_device)
    print(f"  {adapter_for_us.use_in_us()}")

    print("\nUsing US Device in EU:")
    adapter_for_eu = ElectricalAdapter(us_device=us_device)
    print(f"  {adapter_for_eu.use_in_eu()}")


def demo_cloud_storage_adapters():
    """Demonstrate cloud storage adapters."""
    print("\n" + "="*60)
    print("ADAPTER PATTERN - CLOUD STORAGE ADAPTERS")
    print("="*60)

    print("\nAWS S3 Storage:")
    aws = AWSStorage()
    aws.upload("photo.jpg", b"image_data")
    aws.download("photo.jpg")

    print("\nGoogle Cloud Storage (with Adapter):")
    gcs_api = GoogleCloudLegacyAPI()
    gcs_adapter = GoogleCloudAdapter(gcs_api)
    gcs_adapter.upload("photo.jpg", b"image_data")
    gcs_adapter.download("photo.jpg")

    print("\nUnified Storage Interface:")
    storages: List[StorageInterface] = [
        aws,
        gcs_adapter
    ]
    for storage in storages:
        print(f"\nUsing {storage.__class__.__name__}:")
        storage.upload("document.pdf", b"pdf_data")
        storage.download("document.pdf")


def demo_adapter_benefits():
    """Demonstrate adapter pattern benefits."""
    print("\n" + "="*60)
    print("ADAPTER PATTERN - BENEFITS")
    print("="*60)

    print("""
KEY BENEFITS:

1. LEGACY SYSTEM INTEGRATION
   - Use old systems with new interfaces
   - Gradual migration from legacy to modern
   - Don't need to rewrite legacy code

2. THIRD-PARTY LIBRARY INTEGRATION
   - Adapt external libraries to your interface
   - Decouple from external library API
   - Easy to switch libraries later

3. MULTIPLE IMPLEMENTATIONS
   - Support multiple database systems
   - Multiple payment processors
   - Different cloud providers

4. SINGLE RESPONSIBILITY
   - Adapter handles interface conversion only
   - Original code unchanged

5. OPEN/CLOSED PRINCIPLE
   - Add new adapters without modifying existing code
   - Extend functionality through adapters

6. REUSABILITY
   - Reuse existing classes with different interfaces
   - Don't duplicate functionality

7. TESTING
   - Can mock adapters for testing
   - Test adapter implementation separately
    """)


# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

"""
KEY TAKEAWAYS - ADAPTER PATTERN:

1. WHEN TO USE:
   - Incompatible interfaces need to work together
   - Legacy code needs to work with new code
   - Third-party library has incompatible interface
   - Want to support multiple implementations

2. TWO TYPES OF ADAPTERS:
   - Object Adapter: Uses composition (more flexible, recommended)
   - Class Adapter: Uses inheritance (not always possible)

3. ADAPTER vs DECORATOR:
   - Adapter: Converts interface (compatibility)
   - Decorator: Adds behavior (enhancement)
   - Adapter doesn't add functionality, just converts interface

4. ADAPTER vs BRIDGE:
   - Adapter: Retrofitted after design (legacy)
   - Bridge: Planned separation of abstraction/implementation
   - Use Bridge when designing for multiple implementations

5. ADAPTER vs FACADE:
   - Adapter: Makes incompatible interfaces compatible
   - Facade: Simplifies complex interfaces
   - Both can be used together

6. COMMON PATTERNS:
   - Legacy adapter (old to new)
   - API adapter (third-party to internal)
   - Database adapter (multiple database support)
   - Format adapter (different data formats)
   - Hardware adapter (different device interfaces)

7. REAL WORLD EXAMPLES:
   - Database drivers (different database APIs)
   - ORM frameworks (different database systems)
   - API gateways (different payment processors)
   - Hardware interfaces (different device types)
   - Format converters (JSON, XML, CSV)

8. DESIGN GUIDELINES:
   - Clear interface that client expects
   - Minimal adapter implementation
   - Single responsibility
   - Document what interface is being adapted
"""


if __name__ == "__main__":
    demo_legacy_system_integration()
    demo_database_adapters()
    demo_payment_gateway_adapters()
    demo_format_adapters()
    demo_two_way_adapter()
    demo_cloud_storage_adapters()
    demo_adapter_benefits()

    print("\n" + "="*60)
    print("All Adapter Pattern examples completed!")
    print("="*60)
