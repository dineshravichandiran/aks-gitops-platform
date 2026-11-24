"""Optional OpenTelemetry tracing.

Tracing is off unless OTEL_EXPORTER_OTLP_ENDPOINT is set, so the app runs the
same as before when no collector is available. The OpenTelemetry packages are
imported only when tracing is switched on.
"""
import os


def setup_tracing(flask_app, exporter=None) -> bool:
    """Instrument the Flask app and return True if tracing was enabled.

    `exporter` lets tests pass an in-memory exporter. Normally the OTLP/HTTP
    exporter is used and it reads its settings from the standard OTEL_* variables.
    """
    if exporter is None and not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return False

    from opentelemetry import trace
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor

    if exporter is None:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        processor = BatchSpanProcessor(OTLPSpanExporter())
    else:
        processor = SimpleSpanProcessor(exporter)

    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": os.getenv("OTEL_SERVICE_NAME", "demo-app"),
                "service.version": os.getenv("APP_VERSION", "dev"),
            }
        )
    )
    provider.add_span_processor(processor)
    # Pass the provider directly instead of setting the global one, so a second
    # call (for example in tests) does not hit "provider already set".
    FlaskInstrumentor().instrument_app(
        flask_app,
        tracer_provider=provider,
        excluded_urls="healthz,metrics",
    )
    return True
