"""
System Monitoring and Metrics Collection

Comprehensive metrics collection system covering:
- Golden Signals (Latency, Traffic, Errors, Saturation)
- RED Metrics (Rate, Errors, Duration)
- USE Metrics (Utilization, Saturation, Errors)
- Custom business metrics
- Histogram and percentile calculations
- Time-series data collection
- Alerting based on metrics

Author: HLD Course
"""

import time
import threading
import psutil
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
from contextlib import contextmanager
import statistics


# ============================================================================
# Metric Types
# ============================================================================

class Counter:
    """
    Counter metric - monotonically increasing value

    Use for: Request counts, error counts, events

    Example: http_requests_total, errors_total
    """

    def __init__(self, name: str, description: str = "", labels: Dict = None):
        self.name = name
        self.description = description
        self.labels = labels or {}
        self.value = 0
        self.lock = threading.Lock()

    def inc(self, amount: float = 1.0):
        """Increment counter"""
        with self.lock:
            self.value += amount

    def get(self) -> float:
        """Get current value"""
        with self.lock:
            return self.value

    def reset(self):
        """Reset counter to zero"""
        with self.lock:
            self.value = 0


class Gauge:
    """
    Gauge metric - can go up and down

    Use for: Current values, temperatures, memory usage

    Example: memory_usage_bytes, active_connections
    """

    def __init__(self, name: str, description: str = "", labels: Dict = None):
        self.name = name
        self.description = description
        self.labels = labels or {}
        self.value = 0.0
        self.lock = threading.Lock()

    def set(self, value: float):
        """Set gauge value"""
        with self.lock:
            self.value = value

    def inc(self, amount: float = 1.0):
        """Increment gauge"""
        with self.lock:
            self.value += amount

    def dec(self, amount: float = 1.0):
        """Decrement gauge"""
        with self.lock:
            self.value -= amount

    def get(self) -> float:
        """Get current value"""
        with self.lock:
            return self.value


class Histogram:
    """
    Histogram metric - tracks distribution of values

    Use for: Request durations, response sizes

    Provides: Count, sum, and percentiles (p50, p95, p99)

    Example: http_request_duration_seconds
    """

    def __init__(self, name: str, description: str = "", labels: Dict = None):
        self.name = name
        self.description = description
        self.labels = labels or {}
        self.values: deque = deque(maxlen=10000)  # Keep last 10k values
        self.count = 0
        self.sum = 0.0
        self.lock = threading.Lock()

    def observe(self, value: float):
        """Record observation"""
        with self.lock:
            self.values.append(value)
            self.count += 1
            self.sum += value

    def get_count(self) -> int:
        """Get total count of observations"""
        with self.lock:
            return self.count

    def get_sum(self) -> float:
        """Get sum of all observations"""
        with self.lock:
            return self.sum

    def get_percentile(self, percentile: float) -> float:
        """
        Get percentile value (0.0 to 1.0)

        Args:
            percentile: 0.5 for p50, 0.95 for p95, 0.99 for p99
        """
        with self.lock:
            if not self.values:
                return 0.0

            sorted_values = sorted(self.values)
            index = int(len(sorted_values) * percentile)
            return sorted_values[min(index, len(sorted_values) - 1)]

    def get_average(self) -> float:
        """Get average value"""
        with self.lock:
            if self.count == 0:
                return 0.0
            return self.sum / self.count

    def get_stats(self) -> Dict:
        """Get comprehensive statistics"""
        with self.lock:
            if not self.values:
                return {
                    'count': 0,
                    'sum': 0.0,
                    'avg': 0.0,
                    'min': 0.0,
                    'max': 0.0,
                    'p50': 0.0,
                    'p95': 0.0,
                    'p99': 0.0
                }

            sorted_values = sorted(self.values)
            return {
                'count': self.count,
                'sum': self.sum,
                'avg': self.sum / self.count,
                'min': sorted_values[0],
                'max': sorted_values[-1],
                'p50': self._get_percentile_from_sorted(sorted_values, 0.50),
                'p95': self._get_percentile_from_sorted(sorted_values, 0.95),
                'p99': self._get_percentile_from_sorted(sorted_values, 0.99)
            }

    def _get_percentile_from_sorted(self, sorted_values: List[float], percentile: float) -> float:
        """Helper to get percentile from sorted list"""
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]


# ============================================================================
# Metrics Registry
# ============================================================================

class MetricsRegistry:
    """
    Central registry for all metrics

    Provides a single place to register and retrieve metrics.
    """

    def __init__(self):
        self.counters: Dict[str, Counter] = {}
        self.gauges: Dict[str, Gauge] = {}
        self.histograms: Dict[str, Histogram] = {}
        self.lock = threading.Lock()

    def counter(self, name: str, description: str = "", labels: Dict = None) -> Counter:
        """Get or create counter"""
        with self.lock:
            if name not in self.counters:
                self.counters[name] = Counter(name, description, labels)
            return self.counters[name]

    def gauge(self, name: str, description: str = "", labels: Dict = None) -> Gauge:
        """Get or create gauge"""
        with self.lock:
            if name not in self.gauges:
                self.gauges[name] = Gauge(name, description, labels)
            return self.gauges[name]

    def histogram(self, name: str, description: str = "", labels: Dict = None) -> Histogram:
        """Get or create histogram"""
        with self.lock:
            if name not in self.histograms:
                self.histograms[name] = Histogram(name, description, labels)
            return self.histograms[name]

    def get_all_metrics(self) -> Dict:
        """Get all current metric values"""
        with self.lock:
            metrics = {}

            for name, counter in self.counters.items():
                metrics[name] = {'type': 'counter', 'value': counter.get()}

            for name, gauge in self.gauges.items():
                metrics[name] = {'type': 'gauge', 'value': gauge.get()}

            for name, histogram in self.histograms.items():
                metrics[name] = {'type': 'histogram', 'stats': histogram.get_stats()}

            return metrics


# Global metrics registry
metrics_registry = MetricsRegistry()


# ============================================================================
# Golden Signals (Google SRE)
# ============================================================================

class GoldenSignals:
    """
    The Four Golden Signals from Google SRE

    1. Latency - Time to serve a request
    2. Traffic - Demand on the system
    3. Errors - Rate of failed requests
    4. Saturation - Resource utilization
    """

    def __init__(self, registry: MetricsRegistry, service_name: str):
        self.registry = registry
        self.service_name = service_name

        # Latency
        self.latency = registry.histogram(
            f"{service_name}_request_duration_seconds",
            "Request latency in seconds"
        )

        # Traffic
        self.requests_total = registry.counter(
            f"{service_name}_requests_total",
            "Total number of requests"
        )

        # Errors
        self.errors_total = registry.counter(
            f"{service_name}_errors_total",
            "Total number of errors"
        )

        # Saturation
        self.cpu_usage = registry.gauge(
            f"{service_name}_cpu_usage_percent",
            "CPU usage percentage"
        )
        self.memory_usage = registry.gauge(
            f"{service_name}_memory_usage_bytes",
            "Memory usage in bytes"
        )

    @contextmanager
    def track_request(self, success: bool = True):
        """
        Context manager to track request metrics

        Usage:
            with golden_signals.track_request():
                # Handle request
                process_request()
        """
        start_time = time.time()
        self.requests_total.inc()

        try:
            yield
        except Exception as e:
            self.errors_total.inc()
            success = False
            raise
        finally:
            duration = time.time() - start_time
            self.latency.observe(duration)

    def update_saturation(self):
        """Update saturation metrics (CPU, memory)"""
        self.cpu_usage.set(psutil.cpu_percent())
        self.memory_usage.set(psutil.virtual_memory().used)

    def get_metrics(self) -> Dict:
        """Get all golden signal metrics"""
        return {
            'latency': self.latency.get_stats(),
            'traffic': {
                'requests_total': self.requests_total.get()
            },
            'errors': {
                'errors_total': self.errors_total.get(),
                'error_rate': (
                    self.errors_total.get() / max(self.requests_total.get(), 1)
                )
            },
            'saturation': {
                'cpu_percent': self.cpu_usage.get(),
                'memory_bytes': self.memory_usage.get()
            }
        }


# ============================================================================
# RED Metrics (for Services)
# ============================================================================

class REDMetrics:
    """
    RED Metrics for services

    - Rate: Requests per second
    - Errors: Failed requests per second
    - Duration: Response time distribution
    """

    def __init__(self, registry: MetricsRegistry, service_name: str):
        self.registry = registry
        self.service_name = service_name

        self.requests_total = registry.counter(
            f"{service_name}_requests_total",
            "Total requests"
        )
        self.errors_total = registry.counter(
            f"{service_name}_errors_total",
            "Total errors"
        )
        self.duration = registry.histogram(
            f"{service_name}_request_duration_seconds",
            "Request duration"
        )

        # Track requests over time for rate calculation
        self.request_timestamps: deque = deque(maxlen=1000)
        self.lock = threading.Lock()

    @contextmanager
    def track_request(self):
        """Track request with RED metrics"""
        start_time = time.time()

        with self.lock:
            self.request_timestamps.append(start_time)

        self.requests_total.inc()

        try:
            yield
        except Exception as e:
            self.errors_total.inc()
            raise
        finally:
            duration = time.time() - start_time
            self.duration.observe(duration)

    def get_rate(self, window_seconds: float = 60.0) -> float:
        """
        Calculate request rate over time window

        Args:
            window_seconds: Time window to calculate rate

        Returns:
            Requests per second
        """
        with self.lock:
            now = time.time()
            cutoff = now - window_seconds

            recent_requests = [ts for ts in self.request_timestamps if ts >= cutoff]
            return len(recent_requests) / window_seconds

    def get_error_rate(self) -> float:
        """Calculate error rate"""
        total_requests = self.requests_total.get()
        if total_requests == 0:
            return 0.0
        return self.errors_total.get() / total_requests

    def get_metrics(self) -> Dict:
        """Get all RED metrics"""
        return {
            'rate': self.get_rate(),
            'errors': {
                'total': self.errors_total.get(),
                'rate': self.get_error_rate()
            },
            'duration': self.duration.get_stats()
        }


# ============================================================================
# USE Metrics (for Resources)
# ============================================================================

class USEMetrics:
    """
    USE Metrics for resources (CPU, memory, disk, network)

    - Utilization: % time resource is busy
    - Saturation: Queue length or wait time
    - Errors: Error count
    """

    def __init__(self, registry: MetricsRegistry, resource_name: str):
        self.registry = registry
        self.resource_name = resource_name

        self.utilization = registry.gauge(
            f"{resource_name}_utilization_percent",
            "Resource utilization percentage"
        )
        self.saturation = registry.gauge(
            f"{resource_name}_saturation",
            "Resource saturation (queue length)"
        )
        self.errors = registry.counter(
            f"{resource_name}_errors_total",
            "Resource errors"
        )

    def set_utilization(self, percent: float):
        """Set utilization percentage"""
        self.utilization.set(percent)

    def set_saturation(self, value: float):
        """Set saturation value"""
        self.saturation.set(value)

    def inc_errors(self):
        """Increment error count"""
        self.errors.inc()

    def get_metrics(self) -> Dict:
        """Get all USE metrics"""
        return {
            'utilization': self.utilization.get(),
            'saturation': self.saturation.get(),
            'errors': self.errors.get()
        }


# ============================================================================
# System Resource Metrics Collector
# ============================================================================

class SystemMetricsCollector:
    """
    Collects system-level metrics

    - CPU usage
    - Memory usage
    - Disk I/O
    - Network I/O
    """

    def __init__(self, registry: MetricsRegistry):
        self.registry = registry

        # CPU metrics
        self.cpu_percent = registry.gauge("system_cpu_percent", "CPU usage %")
        self.cpu_count = registry.gauge("system_cpu_count", "Number of CPUs")

        # Memory metrics
        self.memory_total = registry.gauge("system_memory_total_bytes", "Total memory")
        self.memory_used = registry.gauge("system_memory_used_bytes", "Used memory")
        self.memory_percent = registry.gauge("system_memory_percent", "Memory usage %")

        # Disk metrics
        self.disk_total = registry.gauge("system_disk_total_bytes", "Total disk space")
        self.disk_used = registry.gauge("system_disk_used_bytes", "Used disk space")
        self.disk_percent = registry.gauge("system_disk_percent", "Disk usage %")

        # Network metrics
        self.network_sent = registry.counter("system_network_sent_bytes", "Bytes sent")
        self.network_recv = registry.counter("system_network_recv_bytes", "Bytes received")

        # Initialize CPU count
        self.cpu_count.set(psutil.cpu_count())

    def collect(self):
        """Collect all system metrics"""
        # CPU
        self.cpu_percent.set(psutil.cpu_percent(interval=0.1))

        # Memory
        memory = psutil.virtual_memory()
        self.memory_total.set(memory.total)
        self.memory_used.set(memory.used)
        self.memory_percent.set(memory.percent)

        # Disk
        disk = psutil.disk_usage('/')
        self.disk_total.set(disk.total)
        self.disk_used.set(disk.used)
        self.disk_percent.set(disk.percent)

        # Network
        network = psutil.net_io_counters()
        self.network_sent.set(network.bytes_sent)
        self.network_recv.set(network.bytes_recv)

    def get_metrics(self) -> Dict:
        """Get all system metrics"""
        return {
            'cpu': {
                'percent': self.cpu_percent.get(),
                'count': self.cpu_count.get()
            },
            'memory': {
                'total_bytes': self.memory_total.get(),
                'used_bytes': self.memory_used.get(),
                'percent': self.memory_percent.get()
            },
            'disk': {
                'total_bytes': self.disk_total.get(),
                'used_bytes': self.disk_used.get(),
                'percent': self.disk_percent.get()
            },
            'network': {
                'sent_bytes': self.network_sent.get(),
                'recv_bytes': self.network_recv.get()
            }
        }


# ============================================================================
# Alerting System
# ============================================================================

@dataclass
class Alert:
    """Alert definition"""
    name: str
    condition: Callable[[], bool]
    severity: str  # critical, warning, info
    message: str
    triggered_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class AlertManager:
    """
    Alert manager

    Evaluates alert conditions and triggers notifications.
    """

    def __init__(self):
        self.alerts: List[Alert] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.lock = threading.Lock()

    def add_alert(self, name: str, condition: Callable[[], bool],
                  severity: str, message: str):
        """Add alert rule"""
        alert = Alert(name, condition, severity, message)
        with self.lock:
            self.alerts.append(alert)

    def evaluate(self):
        """Evaluate all alert conditions"""
        with self.lock:
            for alert in self.alerts:
                is_triggered = alert.condition()

                if is_triggered and alert.name not in self.active_alerts:
                    # Alert triggered
                    alert.triggered_at = datetime.utcnow()
                    self.active_alerts[alert.name] = alert
                    self._trigger_alert(alert)

                elif not is_triggered and alert.name in self.active_alerts:
                    # Alert resolved
                    alert.resolved_at = datetime.utcnow()
                    self._resolve_alert(alert)
                    del self.active_alerts[alert.name]

    def _trigger_alert(self, alert: Alert):
        """Trigger alert (send notification)"""
        print(f"\n🚨 ALERT [{alert.severity.upper()}]: {alert.name}")
        print(f"   {alert.message}")
        print(f"   Triggered at: {alert.triggered_at}")

    def _resolve_alert(self, alert: Alert):
        """Resolve alert"""
        print(f"\n✅ RESOLVED: {alert.name}")
        print(f"   Resolved at: {alert.resolved_at}")

    def get_active_alerts(self) -> List[Alert]:
        """Get list of active alerts"""
        with self.lock:
            return list(self.active_alerts.values())


# ============================================================================
# Demo and Examples
# ============================================================================

def demo_basic_metrics():
    """Demonstrate basic metrics"""
    print("\n" + "=" * 70)
    print("BASIC METRICS")
    print("=" * 70)

    registry = MetricsRegistry()

    # Counter
    requests = registry.counter("http_requests_total", "Total HTTP requests")
    for _ in range(100):
        requests.inc()

    print(f"\nRequests counter: {requests.get()}")

    # Gauge
    temperature = registry.gauge("room_temperature_celsius", "Room temperature")
    temperature.set(22.5)
    temperature.inc(1.5)
    temperature.dec(0.5)

    print(f"Temperature gauge: {temperature.get()}°C")

    # Histogram
    latency = registry.histogram("request_duration_seconds", "Request latency")
    for _ in range(1000):
        latency.observe(random.uniform(0.01, 0.5))

    stats = latency.get_stats()
    print(f"\nLatency histogram:")
    print(f"  Count: {stats['count']}")
    print(f"  Average: {stats['avg']:.4f}s")
    print(f"  p50: {stats['p50']:.4f}s")
    print(f"  p95: {stats['p95']:.4f}s")
    print(f"  p99: {stats['p99']:.4f}s")


def demo_golden_signals():
    """Demonstrate Golden Signals"""
    print("\n" + "=" * 70)
    print("GOLDEN SIGNALS")
    print("=" * 70)

    golden = GoldenSignals(metrics_registry, "api")

    # Simulate requests
    print("\nSimulating 100 requests...")
    for i in range(100):
        success = random.random() > 0.05  # 5% error rate

        try:
            with golden.track_request(success=success):
                # Simulate request processing
                time.sleep(random.uniform(0.01, 0.1))

                if not success:
                    raise Exception("Request failed")

        except Exception:
            pass

    # Update saturation metrics
    golden.update_saturation()

    # Display metrics
    metrics = golden.get_metrics()
    print("\n--- Golden Signals Metrics ---")
    print(f"\nLatency:")
    print(f"  Average: {metrics['latency']['avg']:.4f}s")
    print(f"  p95: {metrics['latency']['p95']:.4f}s")
    print(f"  p99: {metrics['latency']['p99']:.4f}s")

    print(f"\nTraffic:")
    print(f"  Total requests: {metrics['traffic']['requests_total']}")

    print(f"\nErrors:")
    print(f"  Total errors: {metrics['errors']['errors_total']}")
    print(f"  Error rate: {metrics['errors']['error_rate']:.2%}")

    print(f"\nSaturation:")
    print(f"  CPU: {metrics['saturation']['cpu_percent']:.1f}%")
    print(f"  Memory: {metrics['saturation']['memory_bytes'] / 1024**3:.2f} GB")


def demo_system_metrics():
    """Demonstrate system metrics collection"""
    print("\n" + "=" * 70)
    print("SYSTEM METRICS")
    print("=" * 70)

    collector = SystemMetricsCollector(metrics_registry)
    collector.collect()

    metrics = collector.get_metrics()

    print(f"\nCPU:")
    print(f"  Usage: {metrics['cpu']['percent']:.1f}%")
    print(f"  Count: {int(metrics['cpu']['count'])} cores")

    print(f"\nMemory:")
    print(f"  Total: {metrics['memory']['total_bytes'] / 1024**3:.2f} GB")
    print(f"  Used: {metrics['memory']['used_bytes'] / 1024**3:.2f} GB")
    print(f"  Usage: {metrics['memory']['percent']:.1f}%")

    print(f"\nDisk:")
    print(f"  Total: {metrics['disk']['total_bytes'] / 1024**3:.2f} GB")
    print(f"  Used: {metrics['disk']['used_bytes'] / 1024**3:.2f} GB")
    print(f"  Usage: {metrics['disk']['percent']:.1f}%")


def demo_alerting():
    """Demonstrate alerting system"""
    print("\n" + "=" * 70)
    print("ALERTING SYSTEM")
    print("=" * 70)

    golden = GoldenSignals(metrics_registry, "web")
    alert_manager = AlertManager()

    # Define alert rules
    alert_manager.add_alert(
        name="HighErrorRate",
        condition=lambda: (
            golden.errors_total.get() / max(golden.requests_total.get(), 1) > 0.1
        ),
        severity="critical",
        message="Error rate exceeded 10%"
    )

    alert_manager.add_alert(
        name="HighLatency",
        condition=lambda: golden.latency.get_average() > 0.5,
        severity="warning",
        message="Average latency exceeded 500ms"
    )

    # Simulate requests with varying conditions
    print("\nSimulating normal traffic...")
    for _ in range(50):
        with golden.track_request():
            time.sleep(random.uniform(0.01, 0.05))

    alert_manager.evaluate()

    print("\nSimulating high error rate...")
    for _ in range(30):
        try:
            with golden.track_request():
                if random.random() < 0.3:  # 30% error rate
                    raise Exception("Error!")
                time.sleep(0.01)
        except:
            pass

    alert_manager.evaluate()

    print("\nReturning to normal...")
    for _ in range(50):
        with golden.track_request():
            time.sleep(random.uniform(0.01, 0.05))

    alert_manager.evaluate()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SYSTEM MONITORING AND METRICS - COMPREHENSIVE DEMONSTRATION")
    print("=" * 70)

    # Run all demos
    demo_basic_metrics()
    demo_golden_signals()
    demo_system_metrics()
    demo_alerting()

    print("\n" + "=" * 70)
    print("All Demos Complete!")
    print("=" * 70)

    print("\n📝 Key Takeaways:")
    print("1. Use Golden Signals (Latency, Traffic, Errors, Saturation)")
    print("2. Track RED metrics for services (Rate, Errors, Duration)")
    print("3. Monitor USE metrics for resources (Utilization, Saturation, Errors)")
    print("4. Collect percentiles (p50, p95, p99) for better understanding")
    print("5. Set up alerts based on metric thresholds")
    print("6. Monitor both application and system metrics")
    print("7. Use counters for cumulative values")
    print("8. Use gauges for current state")
    print("9. Use histograms for distributions")
    print("10. Aggregate metrics for dashboards and alerting")
    print("=" * 70)
