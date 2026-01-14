import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from core.context import request_id_ctx

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Use existing ID from header (if any), otherwise generate new
        corr_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Set the context variable
        token = request_id_ctx.set(corr_id)
        
        response = await call_next(request)
        
        # Return the ID in response headers for easier debugging
        response.headers["X-Request-ID"] = corr_id
        
        request_id_ctx.reset(token)
        return response