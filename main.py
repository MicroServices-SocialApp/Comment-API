from exc.exceptions import add_exception_handlers
from fastapi import FastAPI
from exc.logging_config import setup_logging
from middleware.correlation import CorrelationIdMiddleware
from router import comment

setup_logging()

# -----------------------------------------------------------------------------------------------

app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)

# -----------------------------------------------------------------------------------------------

app.include_router(comment.router)

# -----------------------------------------------------------------------------------------------

add_exception_handlers(app)