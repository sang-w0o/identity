from spaceone.api.identity.v1 import authorization_pb2, authorization_pb2_grpc
from spaceone.core.pygrpc import BaseAPI
from opentelemetry import trace, propagators
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


class Authorization(BaseAPI, authorization_pb2_grpc.AuthorizationServicer):
    # set_global_textmap(B3Format())
    # propagator = propagate.get_global_textmap()
    pb2 = authorization_pb2
    pb2_grpc = authorization_pb2_grpc
    resource = Resource(attributes={
        SERVICE_NAME: "identity"
    })
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-poc-collector.otel.svc.cluster.local:4317"))
    # processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(__name__)

    # @tracer.start_as_current_span("IdentityService.verify")
    def verify(self, request, context):
        # ctx = self.propagator.extract(header_from_carrier, carrier)
        # with self.tracer.start_as_current_span("BoardService.list", context=ctx) as span:
        with self.tracer.start_as_current_span("BoardService.list") as span:
            print("trace_id: ", span.get_span_context().trace_id)

            params, metadata = self.parse_request(request, context)

            with self.locator.get_service('AuthorizationService', metadata) as auth_service:
                auth_data = auth_service.verify(params)
                return self.locator.get_info('AuthorizationResponse', auth_data)

