from sqlalchemy.exc import IntegrityError, SQLAlchemyError, OperationalError
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from router import abc
import logging

# -----------------------------------------------------------------------------------------------

app = FastAPI()
app.include_router(abc.router)

# -----------------------------------------------------------------------------------------------

logger: logging.Logger = logging.getLogger(__name__)


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    logger.error(f"Database Integrity Error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Data conflict: (likely email or username) already exists."},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Flattens the complex Pydantic errors
    errors = {err['loc'][-1]: err['msg'] for err in exc.errors()}
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": "Validation Error", "errors": errors}
    )

# -----------------------------------------------------------------------------------------------

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.error(f"General Database Error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred. Please try again later."},
    )

@app.exception_handler(Exception)
async def universal_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Uncaught Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A critical server error occurred."}
    )

@app.exception_handler(OperationalError)
async def operational_handler(request: Request, exc: OperationalError) -> JSONResponse:
    logger.critical(f"DB Connection Error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database connection failed. Please check if the DB is running."},
    )

@app.exception_handler(TimeoutError)
async def timeout_handler(request: Request, exc: TimeoutError) -> JSONResponse:
    logger.error(f"Error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={"detail": f"The database took too long to respond. \n{exc}"}
    )
