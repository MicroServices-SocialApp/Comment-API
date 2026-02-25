from middleware.correlation import CorrelationIdMiddleware
from exc.exceptions import add_exception_handlers
from exc.logging_config import setup_logging
from fastapi import FastAPI
from router import comment


# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
# from opentelemetry.instrumentation.logging import LoggingInstrumentor
# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
# from opentelemetry.sdk.trace.export import BatchSpanProcessor
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.resources import Resource
# from opentelemetry import metrics
# from opentelemetry import trace
# # -----------------------------------------------------------------------------------------------

# # 1. Setup OTel BEFORE everything else
# resource = Resource.create({"service.name": "comment-api"}) # Change per repo
# provider = TracerProvider(resource=resource)
# exporter = OTLPSpanExporter(endpoint="http://otel-collector.observability.svc.cluster.local:4317", insecure=True)
# provider.add_span_processor(BatchSpanProcessor(exporter))
# trace.set_tracer_provider(provider)

# # This injects the IDs into your logging records automatically
# LoggingInstrumentor().instrument(set_logging_format=False)

# reader = PeriodicExportingMetricReader(exporter)
# meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
# # This sets the global meter provider
# metrics.set_meter_provider(meter_provider)

setup_logging()

# -----------------------------------------------------------------------------------------------

app = FastAPI(root_path="/comment")
app.add_middleware(CorrelationIdMiddleware)

# -----------------------------------------------------------------------------------------------

# 3. Instrument the FastAPI app
# FastAPIInstrumentor.instrument_app(app)

# -----------------------------------------------------------------------------------------------

app.include_router(comment.router)

# -----------------------------------------------------------------------------------------------

add_exception_handlers(app)