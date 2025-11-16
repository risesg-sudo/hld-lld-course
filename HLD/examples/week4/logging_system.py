"""
Distributed Logging System

Comprehensive logging implementation for distributed systems including:
- Structured logging
- Correlation IDs for request tracing
- Multiple log levels
- Log aggregation
- Centralized logging simulation
- JSON formatting
- Context managers

Author: HLD Course
"""

import json
import logging
import uuid
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import contextmanager
from dataclasses import dataclass, asdict, field
from enum import Enum
import traceback


# ============================================================================
# Log Levels and Configuration
# ============================================================================

class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogConfig:
    """Logging configuration"""
    APP_NAME = "distributed-app"
    ENVIRONMENT = "production"  # production, staging, development
    MIN_LOG_LEVEL = LogLevel.INFO


# ============================================================================
# Correlation ID Context
# ============================================================================

class CorrelationContext:
    """
    Thread-local storage for correlation IDs

    Allows tracking requests across multiple services and function calls.
    Each request gets a unique correlation ID that's included in all logs.
    """

    _thread_local = threading.local()

    @classmethod
    def set_correlation_id(cls, correlation_id: str):
        """Set correlation ID for current thread"""
        cls._thread_local.correlation_id = correlation_id

    @classmethod
    def get_correlation_id(cls) -> Optional[str]:
        """Get correlation ID for current thread"""
        return getattr(cls._thread_local, 'correlation_id', None)

    @classmethod
    def clear(cls):
        """Clear correlation ID"""
        if hasattr(cls._thread_local, 'correlation_id'):
            delattr(cls._thread_local, 'correlation_id')


@contextmanager
def correlation_id_context(correlation_id: Optional[str] = None):
    """
    Context manager for correlation IDs

    Usage:
        with correlation_id_context():
            # All logs in this block will have the same correlation ID
            logger.info("Processing request")
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())

    CorrelationContext.set_correlation_id(correlation_id)
    try:
        yield correlation_id
    finally:
        CorrelationContext.clear()


# ============================================================================
# Structured Log Entry
# ============================================================================

@dataclass
class LogEntry:
    """
    Structured log entry

    Includes all relevant information for distributed logging:
    - Timestamp
    - Level
    - Message
    - Correlation ID
    - Service name
    - Environment
    - Additional context
    """

    timestamp: str
    level: str
    message: str
    service: str
    environment: str
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    host: Optional[str] = None
    thread_id: Optional[int] = None
    function_name: Optional[str] = None
    line_number: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)


# ============================================================================
# Structured Logger
# ============================================================================

class StructuredLogger:
    """
    Structured logger for distributed systems

    Outputs logs in JSON format with rich context including:
    - Correlation IDs for request tracing
    - Service name and environment
    - Thread information
    - Custom context
    """

    def __init__(self, name: str, min_level: LogLevel = LogLevel.INFO):
        """
        Initialize logger

        Args:
            name: Logger name (usually module name)
            min_level: Minimum log level to output
        """
        self.name = name
        self.min_level = min_level
        self.context: Dict[str, Any] = {}

    def set_context(self, **kwargs):
        """
        Set additional context for all logs

        Example:
            logger.set_context(user_id="123", request_id="abc")
        """
        self.context.update(kwargs)

    def clear_context(self):
        """Clear additional context"""
        self.context.clear()

    def _should_log(self, level: LogLevel) -> bool:
        """Check if message should be logged based on level"""
        level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 4
        }
        return level_order[level] >= level_order[self.min_level]

    def _create_log_entry(
        self,
        level: LogLevel,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None
    ) -> LogEntry:
        """Create structured log entry"""
        import socket
        import inspect

        # Get caller information
        frame = inspect.currentframe()
        caller_frame = frame.f_back.f_back if frame and frame.f_back else None
        function_name = caller_frame.f_code.co_name if caller_frame else None
        line_number = caller_frame.f_lineno if caller_frame else None

        # Merge extra data
        merged_extra = {**self.context, **(extra or {})}

        # Format error if present
        error_data = None
        if error:
            error_data = {
                'type': type(error).__name__,
                'message': str(error),
                'traceback': traceback.format_exc()
            }

        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat() + 'Z',
            level=level.value,
            message=message,
            service=LogConfig.APP_NAME,
            environment=LogConfig.ENVIRONMENT,
            correlation_id=CorrelationContext.get_correlation_id(),
            host=socket.gethostname(),
            thread_id=threading.get_ident(),
            function_name=function_name,
            line_number=line_number,
            extra=merged_extra,
            error=error_data
        )

        return entry

    def _output(self, entry: LogEntry):
        """Output log entry (can be overridden for different outputs)"""
        print(entry.to_json())

    def debug(self, message: str, **extra):
        """Log debug message"""
        if self._should_log(LogLevel.DEBUG):
            entry = self._create_log_entry(LogLevel.DEBUG, message, extra)
            self._output(entry)

    def info(self, message: str, **extra):
        """Log info message"""
        if self._should_log(LogLevel.INFO):
            entry = self._create_log_entry(LogLevel.INFO, message, extra)
            self._output(entry)

    def warning(self, message: str, **extra):
        """Log warning message"""
        if self._should_log(LogLevel.WARNING):
            entry = self._create_log_entry(LogLevel.WARNING, message, extra)
            self._output(entry)

    def error(self, message: str, error: Optional[Exception] = None, **extra):
        """Log error message"""
        if self._should_log(LogLevel.ERROR):
            entry = self._create_log_entry(LogLevel.ERROR, message, extra, error)
            self._output(entry)

    def critical(self, message: str, error: Optional[Exception] = None, **extra):
        """Log critical message"""
        if self._should_log(LogLevel.CRITICAL):
            entry = self._create_log_entry(LogLevel.CRITICAL, message, extra, error)
            self._output(entry)


# ============================================================================
# Log Aggregator (Centralized Logging)
# ============================================================================

class LogAggregator:
    """
    Simulates a centralized log aggregator (like ELK, Splunk, etc.)

    In production, this would send logs to a centralized system.
    Here we simulate storage and querying.
    """

    def __init__(self):
        self.logs: list = []
        self.lock = threading.Lock()

    def ingest(self, log_entry: LogEntry):
        """Ingest log entry"""
        with self.lock:
            self.logs.append(log_entry)

    def query(
        self,
        correlation_id: Optional[str] = None,
        level: Optional[str] = None,
        service: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        Query logs

        Args:
            correlation_id: Filter by correlation ID
            level: Filter by log level
            service: Filter by service name
            limit: Maximum number of results

        Returns:
            List of matching log entries
        """
        with self.lock:
            results = self.logs

            if correlation_id:
                results = [log for log in results if log.correlation_id == correlation_id]

            if level:
                results = [log for log in results if log.level == level]

            if service:
                results = [log for log in results if log.service == service]

            return results[:limit]

    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        with self.lock:
            level_counts = {}
            for log in self.logs:
                level_counts[log.level] = level_counts.get(log.level, 0) + 1

            return {
                'total_logs': len(self.logs),
                'level_counts': level_counts,
                'services': list(set(log.service for log in self.logs))
            }


# Global log aggregator instance
log_aggregator = LogAggregator()


class AggregatedLogger(StructuredLogger):
    """
    Logger that sends logs to aggregator

    Extends StructuredLogger to also send logs to centralized aggregator.
    """

    def __init__(self, name: str, aggregator: LogAggregator, min_level: LogLevel = LogLevel.INFO):
        super().__init__(name, min_level)
        self.aggregator = aggregator

    def _output(self, entry: LogEntry):
        """Output to both console and aggregator"""
        # Print to console
        print(entry.to_json())

        # Send to aggregator
        self.aggregator.ingest(entry)


# ============================================================================
# Example Services (Simulating Microservices)
# ============================================================================

class APIService:
    """Simulates an API service"""

    def __init__(self):
        self.logger = AggregatedLogger("api-service", log_aggregator)

    def handle_request(self, user_id: str, endpoint: str):
        """
        Handle API request

        Demonstrates logging throughout request lifecycle with correlation ID
        """
        with correlation_id_context() as correlation_id:
            self.logger.info(
                "Incoming request",
                endpoint=endpoint,
                user_id=user_id,
                method="GET"
            )

            try:
                # Simulate request processing
                time.sleep(0.1)

                # Call another service
                auth_service = AuthService()
                auth_service.authenticate(user_id)

                # Call database service
                db_service = DatabaseService()
                data = db_service.fetch_user_data(user_id)

                self.logger.info(
                    "Request completed successfully",
                    endpoint=endpoint,
                    user_id=user_id,
                    response_time_ms=100
                )

                return {"status": "success", "data": data}

            except Exception as e:
                self.logger.error(
                    "Request failed",
                    error=e,
                    endpoint=endpoint,
                    user_id=user_id
                )
                raise


class AuthService:
    """Simulates an authentication service"""

    def __init__(self):
        self.logger = AggregatedLogger("auth-service", log_aggregator)

    def authenticate(self, user_id: str):
        """Authenticate user"""
        self.logger.info(
            "Authenticating user",
            user_id=user_id
        )

        # Simulate authentication
        time.sleep(0.05)

        self.logger.info(
            "User authenticated successfully",
            user_id=user_id
        )

        return True


class DatabaseService:
    """Simulates a database service"""

    def __init__(self):
        self.logger = AggregatedLogger("database-service", log_aggregator)

    def fetch_user_data(self, user_id: str):
        """Fetch user data from database"""
        self.logger.debug(
            "Executing database query",
            user_id=user_id,
            query="SELECT * FROM users WHERE id = ?"
        )

        # Simulate database query
        time.sleep(0.05)

        self.logger.debug(
            "Database query completed",
            user_id=user_id,
            rows_returned=1,
            query_time_ms=50
        )

        return {"id": user_id, "name": "John Doe", "email": "john@example.com"}


# ============================================================================
# Performance Monitoring with Logging
# ============================================================================

@contextmanager
def log_performance(logger: StructuredLogger, operation: str, **extra):
    """
    Context manager to log performance metrics

    Usage:
        with log_performance(logger, "database_query", table="users"):
            # Perform operation
            result = db.query(...)
    """
    start_time = time.time()
    logger.info(f"Starting {operation}", **extra)

    try:
        yield
        duration = (time.time() - start_time) * 1000  # Convert to ms
        logger.info(
            f"Completed {operation}",
            duration_ms=duration,
            status="success",
            **extra
        )
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(
            f"Failed {operation}",
            error=e,
            duration_ms=duration,
            status="failure",
            **extra
        )
        raise


# ============================================================================
# Audit Logging
# ============================================================================

class AuditLogger:
    """
    Specialized logger for audit events

    Audit logs are critical for security and compliance.
    They track important user actions and system events.
    """

    def __init__(self, aggregator: LogAggregator):
        self.logger = AggregatedLogger("audit", aggregator, LogLevel.INFO)

    def log_event(
        self,
        event_type: str,
        user_id: str,
        action: str,
        resource: str,
        result: str,
        **extra
    ):
        """
        Log audit event

        Args:
            event_type: Type of event (authentication, authorization, data_access, etc.)
            user_id: User who performed action
            action: Action performed (create, read, update, delete)
            resource: Resource affected
            result: Result of action (success, failure)
            **extra: Additional context
        """
        self.logger.info(
            f"Audit: {event_type}",
            event_type=event_type,
            user_id=user_id,
            action=action,
            resource=resource,
            result=result,
            **extra
        )


# ============================================================================
# Demo and Examples
# ============================================================================

def demo_basic_logging():
    """Demonstrate basic structured logging"""
    print("\n" + "=" * 70)
    print("BASIC STRUCTURED LOGGING")
    print("=" * 70)

    logger = StructuredLogger("demo-service")

    logger.info("Application started", version="1.0.0", environment="production")
    logger.debug("Debug information", data={"key": "value"})
    logger.warning("This is a warning", threshold=90, current_value=95)

    try:
        raise ValueError("Something went wrong!")
    except Exception as e:
        logger.error("An error occurred", error=e, context="demo")


def demo_correlation_ids():
    """Demonstrate correlation IDs for request tracing"""
    print("\n" + "=" * 70)
    print("CORRELATION IDS FOR REQUEST TRACING")
    print("=" * 70)

    api_service = APIService()

    # Simulate multiple requests
    print("\n--- Request 1 ---")
    api_service.handle_request("user_123", "/api/profile")

    print("\n--- Request 2 ---")
    api_service.handle_request("user_456", "/api/settings")

    print("\n--- Request 3 ---")
    api_service.handle_request("user_789", "/api/dashboard")


def demo_log_aggregation():
    """Demonstrate log aggregation and querying"""
    print("\n" + "=" * 70)
    print("LOG AGGREGATION AND QUERYING")
    print("=" * 70)

    # Generate some logs
    api_service = APIService()
    api_service.handle_request("user_123", "/api/profile")

    # Query logs
    print("\n--- Query: All logs ---")
    all_logs = log_aggregator.query(limit=5)
    for log in all_logs:
        print(f"{log.level} [{log.service}] {log.message}")

    print("\n--- Query: ERROR level logs ---")
    error_logs = log_aggregator.query(level="ERROR")
    for log in error_logs:
        print(f"{log.level} [{log.service}] {log.message}")

    print("\n--- Query: auth-service logs ---")
    auth_logs = log_aggregator.query(service="auth-service")
    for log in auth_logs:
        print(f"{log.level} [{log.service}] {log.message}")

    print("\n--- Statistics ---")
    stats = log_aggregator.get_stats()
    print(json.dumps(stats, indent=2))


def demo_performance_logging():
    """Demonstrate performance logging"""
    print("\n" + "=" * 70)
    print("PERFORMANCE LOGGING")
    print("=" * 70)

    logger = AggregatedLogger("performance-demo", log_aggregator)

    with log_performance(logger, "api_call", endpoint="/api/users"):
        time.sleep(0.1)  # Simulate API call

    with log_performance(logger, "database_query", table="users"):
        time.sleep(0.05)  # Simulate database query


def demo_audit_logging():
    """Demonstrate audit logging"""
    print("\n" + "=" * 70)
    print("AUDIT LOGGING")
    print("=" * 70)

    audit = AuditLogger(log_aggregator)

    # Log various audit events
    audit.log_event(
        event_type="authentication",
        user_id="user_123",
        action="login",
        resource="system",
        result="success",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0"
    )

    audit.log_event(
        event_type="authorization",
        user_id="user_123",
        action="access",
        resource="/admin/users",
        result="denied",
        reason="insufficient_permissions"
    )

    audit.log_event(
        event_type="data_access",
        user_id="user_456",
        action="read",
        resource="sensitive_document_123",
        result="success",
        document_id="doc_123"
    )

    audit.log_event(
        event_type="data_modification",
        user_id="user_789",
        action="update",
        resource="user_profile",
        result="success",
        fields_modified=["email", "phone"]
    )


def demo_trace_request():
    """Demonstrate full request trace"""
    print("\n" + "=" * 70)
    print("FULL REQUEST TRACE")
    print("=" * 70)

    # Make a request
    api_service = APIService()
    api_service.handle_request("user_999", "/api/profile")

    # Find all logs for this request using correlation ID
    all_logs = log_aggregator.query(limit=1000)
    if all_logs:
        correlation_id = all_logs[-1].correlation_id

        print(f"\n--- Tracing request {correlation_id} ---")
        request_logs = log_aggregator.query(correlation_id=correlation_id)

        for log in request_logs:
            timestamp = log.timestamp.split('T')[1].split('.')[0]
            print(f"{timestamp} | {log.level:8} | {log.service:20} | {log.message}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("DISTRIBUTED LOGGING SYSTEM - COMPREHENSIVE DEMONSTRATION")
    print("=" * 70)

    # Run all demos
    demo_basic_logging()
    demo_correlation_ids()
    demo_log_aggregation()
    demo_performance_logging()
    demo_audit_logging()
    demo_trace_request()

    print("\n" + "=" * 70)
    print("All Demos Complete!")
    print("=" * 70)

    print("\n📝 Key Takeaways:")
    print("1. Use structured logging (JSON) for easy parsing and querying")
    print("2. Include correlation IDs to trace requests across services")
    print("3. Add rich context (user_id, service, environment, etc.)")
    print("4. Centralize logs for aggregation and analysis")
    print("5. Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    print("6. Never log sensitive data (passwords, credit cards, etc.)")
    print("7. Log performance metrics for monitoring")
    print("8. Use audit logs for security and compliance")
    print("9. Include error details and stack traces")
    print("10. Make logs searchable and actionable")
    print("=" * 70)
