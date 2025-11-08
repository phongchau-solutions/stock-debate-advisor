from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# Simplified stubs for demo - import real libraries when installed
class StubMetric:
    """Stub metric for when observability libraries aren't installed."""

    def inc(self) -> None:
        """Increment counter (no-op)."""
        pass

    def set(self, value: float) -> None:
        """Set gauge value (no-op)."""
        pass


try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from prometheus_client import Counter, Gauge

    # Example metrics
    REQUESTS: Counter = Counter("agentic_requests_total", "Total requests processed")  # type: ignore
    LAST_RUN: Gauge = Gauge("agentic_last_run_timestamp", "Last run timestamp")  # type: ignore
    TRACING_AVAILABLE = True
except ImportError:
    logger.warning("OpenTelemetry/Prometheus not installed - using stub metrics")

    REQUESTS = StubMetric()  # type: ignore
    LAST_RUN = StubMetric()  # type: ignore
    TRACING_AVAILABLE = False


def init_tracing(service_name: str, collector_endpoint: Optional[str] = None) -> None:
    """Initialize OpenTelemetry tracing if available, otherwise use stub."""
    if not TRACING_AVAILABLE:
        logger.info("Tracing stub initialized for %s (install opentelemetry-* for real tracing)", service_name)
        return

    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

    resource = Resource.create(attributes={"service.name": service_name})
    provider = TracerProvider(resource=resource)
    # Add a console exporter by default; replace with OTLP exporter to collector in prod
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    logger.info("Tracing initialized for %s", service_name)
