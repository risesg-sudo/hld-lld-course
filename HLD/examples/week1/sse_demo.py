"""
Server-Sent Events (SSE) Demo
==============================

Demonstrates unidirectional server-to-client streaming over HTTP.
Perfect for live updates, notifications, and real-time feeds.

Usage:
    # Start server
    python sse_demo.py

    # Open in browser: http://localhost:8000
    # Or use curl: curl http://localhost:8000/events
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
import threading
from datetime import datetime
import random


class SSEHandler(BaseHTTPRequestHandler):
    """
    HTTP handler that supports Server-Sent Events.
    """

    # Shared data across all connections
    message_counter = 0
    lock = threading.Lock()

    def do_GET(self):
        """Handle GET requests."""
        path = self.path

        if path == '/':
            self.serve_html_page()
        elif path == '/events':
            self.serve_sse_stream()
        elif path == '/stock-prices':
            self.serve_stock_prices()
        elif path == '/notifications':
            self.serve_notifications()
        elif path == '/progress':
            self.serve_progress_updates()
        else:
            self.send_error(404, "Not Found")

    def serve_html_page(self):
        """Serve HTML page with JavaScript SSE client."""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Server-Sent Events Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .section {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        h2 { color: #666; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
        .event {
            padding: 10px;
            margin: 5px 0;
            background: #f9f9f9;
            border-left: 4px solid #4CAF50;
        }
        .timestamp {
            color: #888;
            font-size: 0.9em;
        }
        .status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
        }
        .connected { background: #4CAF50; color: white; }
        .disconnected { background: #f44336; color: white; }
        .stock {
            display: inline-block;
            margin: 10px;
            padding: 15px;
            background: #e3f2fd;
            border-radius: 5px;
            min-width: 150px;
        }
        .price-up { color: #4CAF50; }
        .price-down { color: #f44336; }
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #ddd;
            border-radius: 5px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: #4CAF50;
            transition: width 0.3s;
            text-align: center;
            line-height: 30px;
            color: white;
        }
        button {
            padding: 10px 20px;
            margin: 5px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover { background: #45a049; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Server-Sent Events (SSE) Demo</h1>

        <div class="section">
            <h2>1. Basic Event Stream</h2>
            <p>Status: <span id="status1" class="status disconnected">Disconnected</span></p>
            <button onclick="startBasicStream()">Start Stream</button>
            <button onclick="stopBasicStream()">Stop Stream</button>
            <div id="events1"></div>
        </div>

        <div class="section">
            <h2>2. Stock Prices (Real-time Updates)</h2>
            <p>Status: <span id="status2" class="status disconnected">Disconnected</span></p>
            <button onclick="startStockStream()">Start Stream</button>
            <button onclick="stopStockStream()">Stop Stream</button>
            <div id="stocks"></div>
        </div>

        <div class="section">
            <h2>3. Notifications</h2>
            <p>Status: <span id="status3" class="status disconnected">Disconnected</span></p>
            <button onclick="startNotifications()">Start Notifications</button>
            <button onclick="stopNotifications()">Stop Notifications</button>
            <div id="notifications"></div>
        </div>

        <div class="section">
            <h2>4. Progress Updates</h2>
            <button onclick="startProgress()">Start Task</button>
            <div class="progress-bar">
                <div id="progress-fill" class="progress-fill" style="width: 0%">0%</div>
            </div>
            <p id="progress-status"></p>
        </div>
    </div>

    <script>
        let eventSource1 = null;
        let eventSource2 = null;
        let eventSource3 = null;

        // Basic Event Stream
        function startBasicStream() {
            if (eventSource1) return;

            eventSource1 = new EventSource('/events');

            eventSource1.onopen = () => {
                document.getElementById('status1').textContent = 'Connected';
                document.getElementById('status1').className = 'status connected';
            };

            eventSource1.onmessage = (event) => {
                const data = JSON.parse(event.data);
                addEvent('events1', data);
            };

            eventSource1.onerror = () => {
                document.getElementById('status1').textContent = 'Disconnected';
                document.getElementById('status1').className = 'status disconnected';
                eventSource1.close();
                eventSource1 = null;
            };
        }

        function stopBasicStream() {
            if (eventSource1) {
                eventSource1.close();
                eventSource1 = null;
                document.getElementById('status1').textContent = 'Disconnected';
                document.getElementById('status1').className = 'status disconnected';
            }
        }

        // Stock Prices
        function startStockStream() {
            if (eventSource2) return;

            eventSource2 = new EventSource('/stock-prices');

            eventSource2.onopen = () => {
                document.getElementById('status2').textContent = 'Connected';
                document.getElementById('status2').className = 'status connected';
            };

            eventSource2.addEventListener('stock-update', (event) => {
                const data = JSON.parse(event.data);
                updateStock(data);
            });

            eventSource2.onerror = () => {
                document.getElementById('status2').textContent = 'Disconnected';
                document.getElementById('status2').className = 'status disconnected';
                eventSource2.close();
                eventSource2 = null;
            };
        }

        function stopStockStream() {
            if (eventSource2) {
                eventSource2.close();
                eventSource2 = null;
                document.getElementById('status2').textContent = 'Disconnected';
                document.getElementById('status2').className = 'status disconnected';
            }
        }

        // Notifications
        function startNotifications() {
            if (eventSource3) return;

            eventSource3 = new EventSource('/notifications');

            eventSource3.onopen = () => {
                document.getElementById('status3').textContent = 'Connected';
                document.getElementById('status3').className = 'status connected';
            };

            eventSource3.addEventListener('notification', (event) => {
                const data = JSON.parse(event.data);
                addNotification(data);
            });

            eventSource3.onerror = () => {
                document.getElementById('status3').textContent = 'Disconnected';
                document.getElementById('status3').className = 'status disconnected';
                eventSource3.close();
                eventSource3 = null;
            };
        }

        function stopNotifications() {
            if (eventSource3) {
                eventSource3.close();
                eventSource3 = null;
                document.getElementById('status3').textContent = 'Disconnected';
                document.getElementById('status3').className = 'status disconnected';
            }
        }

        // Progress Updates
        function startProgress() {
            const eventSource = new EventSource('/progress');

            eventSource.addEventListener('progress', (event) => {
                const data = JSON.parse(event.data);
                const fill = document.getElementById('progress-fill');
                fill.style.width = data.progress + '%';
                fill.textContent = data.progress + '%';
                document.getElementById('progress-status').textContent = data.message;
            });

            eventSource.addEventListener('complete', (event) => {
                const data = JSON.parse(event.data);
                document.getElementById('progress-status').textContent = data.message;
                eventSource.close();
            });

            eventSource.onerror = () => {
                eventSource.close();
            };
        }

        // Helper Functions
        function addEvent(containerId, data) {
            const container = document.getElementById(containerId);
            const eventDiv = document.createElement('div');
            eventDiv.className = 'event';
            eventDiv.innerHTML = `
                <div class="timestamp">${data.timestamp}</div>
                <div>${data.message}</div>
                <div>Counter: ${data.counter}</div>
            `;
            container.insertBefore(eventDiv, container.firstChild);

            // Keep only last 10 events
            while (container.children.length > 10) {
                container.removeChild(container.lastChild);
            }
        }

        function updateStock(data) {
            const container = document.getElementById('stocks');
            let stockDiv = document.getElementById('stock-' + data.symbol);

            if (!stockDiv) {
                stockDiv = document.createElement('div');
                stockDiv.id = 'stock-' + data.symbol;
                stockDiv.className = 'stock';
                container.appendChild(stockDiv);
            }

            const priceClass = data.change >= 0 ? 'price-up' : 'price-down';
            const arrow = data.change >= 0 ? '▲' : '▼';

            stockDiv.innerHTML = `
                <strong>${data.symbol}</strong><br>
                <span class="${priceClass}">$${data.price.toFixed(2)} ${arrow}</span><br>
                <small>Change: ${data.change.toFixed(2)}</small>
            `;
        }

        function addNotification(data) {
            const container = document.getElementById('notifications');
            const notifDiv = document.createElement('div');
            notifDiv.className = 'event';
            notifDiv.innerHTML = `
                <div class="timestamp">${data.timestamp}</div>
                <strong>${data.title}</strong>
                <div>${data.message}</div>
            `;
            container.insertBefore(notifDiv, container.firstChild);

            // Keep only last 5 notifications
            while (container.children.length > 5) {
                container.removeChild(container.lastChild);
            }
        }
    </script>
</body>
</html>
        """

        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def serve_sse_stream(self):
        """Serve basic SSE stream with periodic updates."""
        print("[SSE] Client connected to /events")

        # Send SSE headers
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()

        try:
            # Send events every 2 seconds
            for i in range(30):  # Send 30 events
                with self.lock:
                    self.message_counter += 1
                    counter = self.message_counter

                # Prepare event data
                data = {
                    "message": f"Server event #{counter}",
                    "counter": counter,
                    "timestamp": datetime.now().isoformat()
                }

                # Send SSE formatted message
                self.send_sse_message(data)

                time.sleep(2)

        except Exception as e:
            print(f"[SSE] Client disconnected: {e}")

    def serve_stock_prices(self):
        """Serve real-time stock price updates."""
        print("[SSE] Client connected to /stock-prices")

        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()

        # Simulate stock prices
        stocks = {
            'AAPL': 150.00,
            'GOOGL': 2800.00,
            'MSFT': 300.00,
            'AMZN': 3300.00,
        }

        try:
            while True:
                # Update random stock
                symbol = random.choice(list(stocks.keys()))
                old_price = stocks[symbol]

                # Random price change (-5% to +5%)
                change = random.uniform(-old_price * 0.05, old_price * 0.05)
                new_price = old_price + change
                stocks[symbol] = new_price

                data = {
                    "symbol": symbol,
                    "price": new_price,
                    "change": change,
                    "timestamp": datetime.now().isoformat()
                }

                # Send as named event
                self.send_sse_message(data, event='stock-update')

                time.sleep(1)

        except Exception as e:
            print(f"[SSE] Stock stream client disconnected: {e}")

    def serve_notifications(self):
        """Serve random notifications."""
        print("[SSE] Client connected to /notifications")

        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()

        notifications = [
            ("New Message", "You have a new message from John"),
            ("Friend Request", "Sarah wants to connect with you"),
            ("Like", "Someone liked your post"),
            ("Comment", "New comment on your photo"),
            ("System Update", "System will restart in 10 minutes"),
        ]

        try:
            for i in range(10):
                title, message = random.choice(notifications)

                data = {
                    "title": title,
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                }

                self.send_sse_message(data, event='notification')

                time.sleep(random.uniform(3, 8))

        except Exception as e:
            print(f"[SSE] Notification client disconnected: {e}")

    def serve_progress_updates(self):
        """Serve progress updates for a long-running task."""
        print("[SSE] Client connected to /progress")

        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()

        try:
            # Simulate task progress
            for progress in range(0, 101, 10):
                data = {
                    "progress": progress,
                    "message": f"Processing... {progress}%"
                }

                self.send_sse_message(data, event='progress')
                time.sleep(0.5)

            # Send completion event
            completion_data = {
                "message": "Task completed successfully!"
            }
            self.send_sse_message(completion_data, event='complete')

        except Exception as e:
            print(f"[SSE] Progress client disconnected: {e}")

    def send_sse_message(self, data, event=None, retry=None):
        """
        Send a Server-Sent Event message.

        SSE Format:
        event: event-name
        data: {"key": "value"}
        id: 123
        retry: 10000

        """
        try:
            # Event name (optional)
            if event:
                self.wfile.write(f"event: {event}\n".encode('utf-8'))

            # Data (required)
            json_data = json.dumps(data)
            self.wfile.write(f"data: {json_data}\n".encode('utf-8'))

            # Retry timeout (optional)
            if retry:
                self.wfile.write(f"retry: {retry}\n".encode('utf-8'))

            # Blank line to indicate end of event
            self.wfile.write("\n".encode('utf-8'))

            # Flush the buffer
            self.wfile.flush()

        except Exception as e:
            raise e

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def run_server(port=8000):
    """Run the SSE server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SSEHandler)

    print(f"""
╔════════════════════════════════════════════════════╗
║      Server-Sent Events (SSE) Demo Server          ║
╚════════════════════════════════════════════════════╝

Server running on http://localhost:{port}

SSE Features Demonstrated:
✓ Unidirectional server-to-client streaming
✓ Built on HTTP (works with existing infrastructure)
✓ Auto-reconnection
✓ Named events
✓ Event IDs for resume support
✓ Text-based (UTF-8)

Available Endpoints:
- http://localhost:{port}/              (Interactive demo page)
- http://localhost:{port}/events        (Basic event stream)
- http://localhost:{port}/stock-prices  (Stock price updates)
- http://localhost:{port}/notifications (Random notifications)
- http://localhost:{port}/progress      (Progress updates)

Open http://localhost:{port}/ in your browser!

Press Ctrl+C to stop the server.
    """)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n[SERVER] Shutting down...")
        httpd.shutdown()


if __name__ == '__main__':
    run_server(port=8000)
