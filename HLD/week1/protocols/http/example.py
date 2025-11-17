"""
HTTP Request/Response Handling Demo
====================================

Demonstrates HTTP concepts including:
- HTTP methods (GET, POST, PUT, DELETE)
- Status codes
- Headers
- Request/Response structure
- Simple REST API

Usage:
    # Start server
    python http_example.py

    # Test with curl:
    curl http://localhost:8000/api/users
    curl -X POST -H "Content-Type: application/json" -d '{"name":"John"}' http://localhost:8000/api/users
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime


# In-memory data store
users_db = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "created_at": "2025-01-01"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "created_at": "2025-01-02"},
}
next_user_id = 3


class HTTPRequestHandler(BaseHTTPRequestHandler):
    """
    Custom HTTP request handler demonstrating REST API implementation.
    """

    def do_GET(self):
        """
        Handle GET requests.
        GET is used to retrieve resources.
        """
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query_params = urllib.parse.parse_qs(parsed_path.query)

        print(f"\n[GET] {path}")
        print(f"[HEADERS] {dict(self.headers)}")

        if path == '/':
            self.send_html_response(200, self.get_homepage_html())

        elif path == '/api/users':
            # Get all users with optional filtering
            self.handle_get_users(query_params)

        elif path.startswith('/api/users/'):
            # Get specific user
            user_id = self.extract_id_from_path(path, '/api/users/')
            self.handle_get_user(user_id)

        elif path == '/api/info':
            # Server information
            self.handle_server_info()

        else:
            self.send_json_response(404, {
                "error": "Not Found",
                "message": f"Path {path} not found"
            })

    def do_POST(self):
        """
        Handle POST requests.
        POST is used to create new resources.
        """
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        print(f"\n[POST] {path}")
        print(f"[HEADERS] {dict(self.headers)}")

        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        print(f"[BODY] {body}")

        if path == '/api/users':
            self.handle_create_user(body)
        else:
            self.send_json_response(404, {
                "error": "Not Found",
                "message": f"Path {path} not found"
            })

    def do_PUT(self):
        """
        Handle PUT requests.
        PUT is used to update existing resources.
        """
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        print(f"\n[PUT] {path}")

        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        if path.startswith('/api/users/'):
            user_id = self.extract_id_from_path(path, '/api/users/')
            self.handle_update_user(user_id, body)
        else:
            self.send_json_response(404, {
                "error": "Not Found",
                "message": f"Path {path} not found"
            })

    def do_DELETE(self):
        """
        Handle DELETE requests.
        DELETE is used to remove resources.
        """
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        print(f"\n[DELETE] {path}")

        if path.startswith('/api/users/'):
            user_id = self.extract_id_from_path(path, '/api/users/')
            self.handle_delete_user(user_id)
        else:
            self.send_json_response(404, {
                "error": "Not Found",
                "message": f"Path {path} not found"
            })

    def do_OPTIONS(self):
        """
        Handle OPTIONS requests (CORS preflight).
        """
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    # Handler methods for different operations

    def handle_get_users(self, query_params):
        """Get all users with optional filtering."""
        users = list(users_db.values())

        # Simple filtering by name
        if 'name' in query_params:
            name_filter = query_params['name'][0].lower()
            users = [u for u in users if name_filter in u['name'].lower()]

        response = {
            "data": users,
            "count": len(users),
            "timestamp": datetime.now().isoformat()
        }

        self.send_json_response(200, response)

    def handle_get_user(self, user_id):
        """Get a specific user by ID."""
        if user_id in users_db:
            self.send_json_response(200, {
                "data": users_db[user_id]
            })
        else:
            self.send_json_response(404, {
                "error": "Not Found",
                "message": f"User with id {user_id} not found"
            })

    def handle_create_user(self, body):
        """Create a new user."""
        global next_user_id

        try:
            data = json.loads(body)

            # Validate required fields
            if 'name' not in data:
                self.send_json_response(400, {
                    "error": "Bad Request",
                    "message": "Field 'name' is required"
                })
                return

            # Create new user
            new_user = {
                "id": next_user_id,
                "name": data['name'],
                "email": data.get('email', ''),
                "created_at": datetime.now().isoformat()
            }

            users_db[next_user_id] = new_user
            next_user_id += 1

            # Return 201 Created with Location header
            self.send_response(201)
            self.send_header('Location', f'/api/users/{new_user["id"]}')
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()

            response = {
                "message": "User created successfully",
                "data": new_user
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

        except json.JSONDecodeError:
            self.send_json_response(400, {
                "error": "Bad Request",
                "message": "Invalid JSON in request body"
            })

    def handle_update_user(self, user_id, body):
        """Update an existing user."""
        if user_id not in users_db:
            self.send_json_response(404, {
                "error": "Not Found",
                "message": f"User with id {user_id} not found"
            })
            return

        try:
            data = json.loads(body)

            # Update user fields
            user = users_db[user_id]
            if 'name' in data:
                user['name'] = data['name']
            if 'email' in data:
                user['email'] = data['email']

            user['updated_at'] = datetime.now().isoformat()

            self.send_json_response(200, {
                "message": "User updated successfully",
                "data": user
            })

        except json.JSONDecodeError:
            self.send_json_response(400, {
                "error": "Bad Request",
                "message": "Invalid JSON in request body"
            })

    def handle_delete_user(self, user_id):
        """Delete a user."""
        if user_id in users_db:
            deleted_user = users_db.pop(user_id)
            self.send_json_response(200, {
                "message": "User deleted successfully",
                "data": deleted_user
            })
        else:
            self.send_json_response(404, {
                "error": "Not Found",
                "message": f"User with id {user_id} not found"
            })

    def handle_server_info(self):
        """Return server information."""
        info = {
            "server": "HTTP Example Server",
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "endpoints": {
                "GET /api/users": "Get all users",
                "GET /api/users/:id": "Get user by ID",
                "POST /api/users": "Create new user",
                "PUT /api/users/:id": "Update user",
                "DELETE /api/users/:id": "Delete user",
                "GET /api/info": "Server information"
            }
        }
        self.send_json_response(200, info)

    # Utility methods

    def extract_id_from_path(self, path, prefix):
        """Extract ID from URL path."""
        try:
            id_str = path[len(prefix):]
            return int(id_str)
        except ValueError:
            return None

    def send_json_response(self, status_code, data):
        """Send JSON response with appropriate headers."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()

        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))

        print(f"[RESPONSE] {status_code}")
        print(f"[RESPONSE BODY] {response_json}")

    def send_html_response(self, status_code, html):
        """Send HTML response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def send_cors_headers(self):
        """Send CORS headers to allow cross-origin requests."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def get_homepage_html(self):
        """Return HTML homepage."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>HTTP Example Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        pre { background: #f4f4f4; padding: 10px; border-radius: 5px; }
        .endpoint { margin: 20px 0; }
    </style>
</head>
<body>
    <h1>HTTP Example Server</h1>
    <p>Simple REST API demonstrating HTTP methods and status codes.</p>

    <h2>Available Endpoints:</h2>

    <div class="endpoint">
        <h3>GET /api/users</h3>
        <pre>curl http://localhost:8000/api/users</pre>
        <p>Get all users. Supports ?name=filter query parameter.</p>
    </div>

    <div class="endpoint">
        <h3>GET /api/users/:id</h3>
        <pre>curl http://localhost:8000/api/users/1</pre>
        <p>Get a specific user by ID.</p>
    </div>

    <div class="endpoint">
        <h3>POST /api/users</h3>
        <pre>curl -X POST -H "Content-Type: application/json" \\
     -d '{"name":"John","email":"john@example.com"}' \\
     http://localhost:8000/api/users</pre>
        <p>Create a new user.</p>
    </div>

    <div class="endpoint">
        <h3>PUT /api/users/:id</h3>
        <pre>curl -X PUT -H "Content-Type: application/json" \\
     -d '{"name":"John Updated"}' \\
     http://localhost:8000/api/users/1</pre>
        <p>Update an existing user.</p>
    </div>

    <div class="endpoint">
        <h3>DELETE /api/users/:id</h3>
        <pre>curl -X DELETE http://localhost:8000/api/users/1</pre>
        <p>Delete a user.</p>
    </div>

    <h2>HTTP Status Codes Used:</h2>
    <ul>
        <li><strong>200 OK</strong> - Successful GET, PUT, DELETE</li>
        <li><strong>201 Created</strong> - Successful POST</li>
        <li><strong>400 Bad Request</strong> - Invalid input</li>
        <li><strong>404 Not Found</strong> - Resource not found</li>
        <li><strong>500 Internal Server Error</strong> - Server error</li>
    </ul>

    <h2>Common Headers:</h2>
    <ul>
        <li><strong>Content-Type</strong> - application/json</li>
        <li><strong>Location</strong> - URL of created resource (201 response)</li>
        <li><strong>Access-Control-Allow-Origin</strong> - CORS header</li>
    </ul>
</body>
</html>
        """

    def log_message(self, format, *args):
        """Override to customize logging."""
        # Custom log format
        pass  # We're printing custom logs in do_* methods


def run_server(port=8000):
    """Run the HTTP server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, HTTPRequestHandler)

    print(f"""
    ╔════════════════════════════════════════════════════╗
    ║        HTTP Example Server Started                 ║
    ╚════════════════════════════════════════════════════╝

    Server running on http://localhost:{port}

    HTTP Concepts Demonstrated:
    ✓ HTTP Methods: GET, POST, PUT, DELETE
    ✓ Status Codes: 200, 201, 400, 404
    ✓ Headers: Content-Type, Location, CORS
    ✓ Request/Response structure
    ✓ REST API design
    ✓ Query parameters
    ✓ JSON payloads

    Try these commands:
    1. Open browser: http://localhost:{port}
    2. Get users:    curl http://localhost:{port}/api/users
    3. Get user:     curl http://localhost:{port}/api/users/1
    4. Create user:  curl -X POST -H "Content-Type: application/json" \\
                          -d '{{"name":"John"}}' http://localhost:{port}/api/users

    Press Ctrl+C to stop the server.
    """)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n[SERVER] Shutting down...")
        httpd.shutdown()


if __name__ == '__main__':
    run_server(port=8000)
