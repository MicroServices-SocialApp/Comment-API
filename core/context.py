from contextvars import ContextVar

# This holds the ID for the duration of one request
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="n/a")