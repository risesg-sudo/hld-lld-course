"""
Microservices Architecture Demo
================================

Demonstrates a simple microservices architecture with:
- User Service
- Product Service
- Order Service
- API Gateway
- Service Discovery (simplified)
- Inter-service communication

This is a simplified demo running all services in one process.
In production, each service would run separately.

Requirements:
    pip install flask requests

Usage:
    python microservices_example.py
"""

from flask import Flask, jsonify, request
import threading
import time
import requests
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(name)s] %(message)s'
)


# ============================================================================
# Service Registry (Simplified Service Discovery)
# ============================================================================

class ServiceRegistry:
    """
    Simple service registry for service discovery.
    In production, use Consul, Eureka, or etcd.
    """

    def __init__(self):
        self.services = {}
        self.lock = threading.Lock()

    def register(self, service_name, host, port):
        """Register a service."""
        with self.lock:
            self.services[service_name] = {
                'host': host,
                'port': port,
                'url': f'http://{host}:{port}',
                'registered_at': datetime.now().isoformat()
            }
        logging.info(f"ServiceRegistry: Registered {service_name} at {host}:{port}")

    def discover(self, service_name):
        """Discover a service."""
        with self.lock:
            service = self.services.get(service_name)
            if service:
                return service['url']
            return None

    def list_services(self):
        """List all registered services."""
        with self.lock:
            return dict(self.services)


# Global service registry
registry = ServiceRegistry()


# ============================================================================
# User Service
# ============================================================================

class UserService:
    """
    User Service - Manages user data and authentication.
    Database: User information
    """

    def __init__(self, port=5001):
        self.app = Flask('UserService')
        self.port = port
        self.logger = logging.getLogger('UserService')

        # In-memory user database
        self.users = {
            1: {"id": 1, "name": "Alice", "email": "alice@example.com", "balance": 1000.0},
            2: {"id": 2, "name": "Bob", "email": "bob@example.com", "balance": 500.0},
            3: {"id": 3, "name": "Charlie", "email": "charlie@example.com", "balance": 750.0},
        }

        self.setup_routes()

    def setup_routes(self):
        """Setup Flask routes."""

        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({"status": "healthy", "service": "UserService"})

        @self.app.route('/users', methods=['GET'])
        def get_users():
            self.logger.info("GET /users")
            return jsonify(list(self.users.values()))

        @self.app.route('/users/<int:user_id>', methods=['GET'])
        def get_user(user_id):
            self.logger.info(f"GET /users/{user_id}")
            user = self.users.get(user_id)
            if user:
                return jsonify(user)
            return jsonify({"error": "User not found"}), 404

        @self.app.route('/users/<int:user_id>/deduct', methods=['POST'])
        def deduct_balance(user_id):
            """Deduct amount from user balance (for orders)."""
            data = request.json
            amount = data.get('amount', 0)

            self.logger.info(f"POST /users/{user_id}/deduct - Amount: {amount}")

            user = self.users.get(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404

            if user['balance'] < amount:
                return jsonify({"error": "Insufficient balance"}), 400

            user['balance'] -= amount
            return jsonify({"success": True, "new_balance": user['balance']})

    def run(self):
        """Run the service."""
        # Register with service registry
        registry.register('user-service', 'localhost', self.port)

        # Run Flask app
        self.logger.info(f"Starting on port {self.port}")
        self.app.run(port=self.port, debug=False, use_reloader=False)


# ============================================================================
# Product Service
# ============================================================================

class ProductService:
    """
    Product Service - Manages product catalog.
    Database: Product information
    """

    def __init__(self, port=5002):
        self.app = Flask('ProductService')
        self.port = port
        self.logger = logging.getLogger('ProductService')

        # In-memory product database
        self.products = {
            101: {"id": 101, "name": "Laptop", "price": 999.99, "stock": 10},
            102: {"id": 102, "name": "Mouse", "price": 29.99, "stock": 50},
            103: {"id": 103, "name": "Keyboard", "price": 79.99, "stock": 30},
        }

        self.setup_routes()

    def setup_routes(self):
        """Setup Flask routes."""

        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({"status": "healthy", "service": "ProductService"})

        @self.app.route('/products', methods=['GET'])
        def get_products():
            self.logger.info("GET /products")
            return jsonify(list(self.products.values()))

        @self.app.route('/products/<int:product_id>', methods=['GET'])
        def get_product(product_id):
            self.logger.info(f"GET /products/{product_id}")
            product = self.products.get(product_id)
            if product:
                return jsonify(product)
            return jsonify({"error": "Product not found"}), 404

        @self.app.route('/products/<int:product_id>/reserve', methods=['POST'])
        def reserve_stock(product_id):
            """Reserve product stock (for orders)."""
            data = request.json
            quantity = data.get('quantity', 0)

            self.logger.info(f"POST /products/{product_id}/reserve - Quantity: {quantity}")

            product = self.products.get(product_id)
            if not product:
                return jsonify({"error": "Product not found"}), 404

            if product['stock'] < quantity:
                return jsonify({"error": "Insufficient stock"}), 400

            product['stock'] -= quantity
            return jsonify({"success": True, "remaining_stock": product['stock']})

    def run(self):
        """Run the service."""
        # Register with service registry
        registry.register('product-service', 'localhost', self.port)

        # Run Flask app
        self.logger.info(f"Starting on port {self.port}")
        self.app.run(port=self.port, debug=False, use_reloader=False)


# ============================================================================
# Order Service
# ============================================================================

class OrderService:
    """
    Order Service - Manages orders and coordinates with other services.
    Database: Order information
    Communication: Calls User Service and Product Service
    """

    def __init__(self, port=5003):
        self.app = Flask('OrderService')
        self.port = port
        self.logger = logging.getLogger('OrderService')

        # In-memory order database
        self.orders = {}
        self.next_order_id = 1

        self.setup_routes()

    def setup_routes(self):
        """Setup Flask routes."""

        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({"status": "healthy", "service": "OrderService"})

        @self.app.route('/orders', methods=['GET'])
        def get_orders():
            self.logger.info("GET /orders")
            return jsonify(list(self.orders.values()))

        @self.app.route('/orders/<int:order_id>', methods=['GET'])
        def get_order(order_id):
            self.logger.info(f"GET /orders/{order_id}")
            order = self.orders.get(order_id)
            if order:
                return jsonify(order)
            return jsonify({"error": "Order not found"}), 404

        @self.app.route('/orders', methods=['POST'])
        def create_order():
            """
            Create an order - demonstrates inter-service communication.
            Saga pattern for distributed transaction.
            """
            data = request.json
            user_id = data.get('user_id')
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)

            self.logger.info(f"POST /orders - User: {user_id}, Product: {product_id}, Qty: {quantity}")

            try:
                # Step 1: Get product details
                product_url = registry.discover('product-service')
                if not product_url:
                    return jsonify({"error": "Product service not available"}), 503

                product_response = requests.get(f"{product_url}/products/{product_id}")
                if product_response.status_code != 200:
                    return jsonify({"error": "Product not found"}), 404

                product = product_response.json()
                total_amount = product['price'] * quantity

                # Step 2: Check user balance
                user_url = registry.discover('user-service')
                if not user_url:
                    return jsonify({"error": "User service not available"}), 503

                user_response = requests.get(f"{user_url}/users/{user_id}")
                if user_response.status_code != 200:
                    return jsonify({"error": "User not found"}), 404

                user = user_response.json()
                if user['balance'] < total_amount:
                    return jsonify({"error": "Insufficient balance"}), 400

                # Step 3: Reserve product stock
                reserve_response = requests.post(
                    f"{product_url}/products/{product_id}/reserve",
                    json={"quantity": quantity}
                )
                if reserve_response.status_code != 200:
                    return jsonify({"error": "Failed to reserve stock"}), 400

                # Step 4: Deduct user balance
                deduct_response = requests.post(
                    f"{user_url}/users/{user_id}/deduct",
                    json={"amount": total_amount}
                )
                if deduct_response.status_code != 200:
                    # Rollback: Return stock
                    self.logger.error("Failed to deduct balance, rolling back stock")
                    # In real system, implement proper compensation
                    return jsonify({"error": "Failed to process payment"}), 400

                # Step 5: Create order
                order = {
                    "id": self.next_order_id,
                    "user_id": user_id,
                    "product_id": product_id,
                    "product_name": product['name'],
                    "quantity": quantity,
                    "total_amount": total_amount,
                    "status": "confirmed",
                    "created_at": datetime.now().isoformat()
                }

                self.orders[self.next_order_id] = order
                self.next_order_id += 1

                self.logger.info(f"Order {order['id']} created successfully")
                return jsonify(order), 201

            except requests.RequestException as e:
                self.logger.error(f"Service communication error: {e}")
                return jsonify({"error": "Service unavailable"}), 503

    def run(self):
        """Run the service."""
        # Register with service registry
        registry.register('order-service', 'localhost', self.port)

        # Run Flask app
        self.logger.info(f"Starting on port {self.port}")
        self.app.run(port=self.port, debug=False, use_reloader=False)


# ============================================================================
# API Gateway
# ============================================================================

class APIGateway:
    """
    API Gateway - Single entry point for all client requests.
    Responsibilities:
    - Routing
    - Authentication (simplified here)
    - Rate limiting (not implemented)
    - Request aggregation
    """

    def __init__(self, port=5000):
        self.app = Flask('APIGateway')
        self.port = port
        self.logger = logging.getLogger('APIGateway')

        self.setup_routes()

    def setup_routes(self):
        """Setup Flask routes."""

        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({"status": "healthy", "service": "APIGateway"})

        @self.app.route('/api/services', methods=['GET'])
        def list_services():
            """List all registered services."""
            return jsonify(registry.list_services())

        # User routes (proxy to User Service)
        @self.app.route('/api/users', methods=['GET'])
        def get_users():
            self.logger.info("Routing GET /api/users -> UserService")
            service_url = registry.discover('user-service')
            if not service_url:
                return jsonify({"error": "User service not available"}), 503

            try:
                response = requests.get(f"{service_url}/users")
                return jsonify(response.json()), response.status_code
            except requests.RequestException as e:
                return jsonify({"error": str(e)}), 503

        @self.app.route('/api/users/<int:user_id>', methods=['GET'])
        def get_user(user_id):
            self.logger.info(f"Routing GET /api/users/{user_id} -> UserService")
            service_url = registry.discover('user-service')
            if not service_url:
                return jsonify({"error": "User service not available"}), 503

            try:
                response = requests.get(f"{service_url}/users/{user_id}")
                return jsonify(response.json()), response.status_code
            except requests.RequestException as e:
                return jsonify({"error": str(e)}), 503

        # Product routes (proxy to Product Service)
        @self.app.route('/api/products', methods=['GET'])
        def get_products():
            self.logger.info("Routing GET /api/products -> ProductService")
            service_url = registry.discover('product-service')
            if not service_url:
                return jsonify({"error": "Product service not available"}), 503

            try:
                response = requests.get(f"{service_url}/products")
                return jsonify(response.json()), response.status_code
            except requests.RequestException as e:
                return jsonify({"error": str(e)}), 503

        @self.app.route('/api/products/<int:product_id>', methods=['GET'])
        def get_product(product_id):
            self.logger.info(f"Routing GET /api/products/{product_id} -> ProductService")
            service_url = registry.discover('product-service')
            if not service_url:
                return jsonify({"error": "Product service not available"}), 503

            try:
                response = requests.get(f"{service_url}/products/{product_id}")
                return jsonify(response.json()), response.status_code
            except requests.RequestException as e:
                return jsonify({"error": str(e)}), 503

        # Order routes (proxy to Order Service)
        @self.app.route('/api/orders', methods=['GET', 'POST'])
        def orders():
            self.logger.info(f"Routing {request.method} /api/orders -> OrderService")
            service_url = registry.discover('order-service')
            if not service_url:
                return jsonify({"error": "Order service not available"}), 503

            try:
                if request.method == 'GET':
                    response = requests.get(f"{service_url}/orders")
                else:  # POST
                    response = requests.post(
                        f"{service_url}/orders",
                        json=request.json
                    )
                return jsonify(response.json()), response.status_code
            except requests.RequestException as e:
                return jsonify({"error": str(e)}), 503

        @self.app.route('/api/orders/<int:order_id>', methods=['GET'])
        def get_order(order_id):
            self.logger.info(f"Routing GET /api/orders/{order_id} -> OrderService")
            service_url = registry.discover('order-service')
            if not service_url:
                return jsonify({"error": "Order service not available"}), 503

            try:
                response = requests.get(f"{service_url}/orders/{order_id}")
                return jsonify(response.json()), response.status_code
            except requests.RequestException as e:
                return jsonify({"error": str(e)}), 503

    def run(self):
        """Run the API Gateway."""
        self.logger.info(f"Starting on port {self.port}")
        self.app.run(port=self.port, debug=False, use_reloader=False)


# ============================================================================
# Main - Start All Services
# ============================================================================

def start_service(service_class, *args, **kwargs):
    """Start a service in a separate thread."""
    service = service_class(*args, **kwargs)
    thread = threading.Thread(target=service.run, daemon=True)
    thread.start()
    return thread


def main():
    """Start all microservices."""
    print("""
╔════════════════════════════════════════════════════════════════╗
║         Microservices Architecture Demo                       ║
╚════════════════════════════════════════════════════════════════╝

Starting services...
    """)

    # Start all services
    threads = []

    # Give services time to start
    print("[MAIN] Starting User Service...")
    threads.append(start_service(UserService, port=5001))
    time.sleep(1)

    print("[MAIN] Starting Product Service...")
    threads.append(start_service(ProductService, port=5002))
    time.sleep(1)

    print("[MAIN] Starting Order Service...")
    threads.append(start_service(OrderService, port=5003))
    time.sleep(1)

    print("[MAIN] Starting API Gateway...")
    threads.append(start_service(APIGateway, port=5000))
    time.sleep(2)

    print("""
╔════════════════════════════════════════════════════════════════╗
║              All Services Started!                             ║
╚════════════════════════════════════════════════════════════════╝

Architecture:

┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   API Gateway       │ (Port 5000)
│   - Routing         │
│   - Auth            │
│   - Aggregation     │
└──────┬──────────────┘
       │
       ├──────────────────┬─────────────────┐
       ▼                  ▼                 ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│User Service  │   │Product Svc   │   │Order Service │
│(Port 5001)   │   │(Port 5002)   │   │(Port 5003)   │
│              │   │              │   │              │
│- Users DB    │   │- Products DB │   │- Orders DB   │
└──────────────┘   └──────────────┘   └──────────────┘

API Endpoints (via Gateway):

GET  http://localhost:5000/api/services       - List services
GET  http://localhost:5000/api/users          - List users
GET  http://localhost:5000/api/users/1        - Get user
GET  http://localhost:5000/api/products       - List products
GET  http://localhost:5000/api/products/101   - Get product
POST http://localhost:5000/api/orders         - Create order
GET  http://localhost:5000/api/orders         - List orders

Example: Create an order:
curl -X POST http://localhost:5000/api/orders \\
     -H "Content-Type: application/json" \\
     -d '{"user_id": 1, "product_id": 101, "quantity": 1}'

Press Ctrl+C to stop all services.
    """)

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[MAIN] Shutting down all services...")


if __name__ == '__main__':
    main()
