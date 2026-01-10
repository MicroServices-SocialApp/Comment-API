from sqlalchemy.exc import (
    AwaitRequired,
    MissingGreenlet,
    IllegalStateChangeError,
    MultipleResultsFound,
    NoResultFound,
    ObjectNotExecutableError,
    UnboundExecutionError,
    ArgumentError,
    InvalidRequestError,
    NoSuchTableError,
    NoSuchColumnError,
    NoReferencedTableError,
    UnreflectableTableError,
    DuplicateColumnError,
    AmbiguousForeignKeysError,
    CircularDependencyError,
    NoForeignKeysError,
    NoReferenceError,
    NoReferencedColumnError,
    ConstraintColumnNotFoundError,
    UnsupportedCompilationError,
    CompileError,
    NoInspectionAvailable,
    OperationalError,
    DisconnectionError,
    InvalidatePoolError,
    InterfaceError,
    TimeoutError,
    NoSuchModuleError,
    IntegrityError,
    DataError,
    IdentifierError,
    ProgrammingError,
    InternalError,
    NotSupportedError,
    PendingRollbackError,
    StatementError,
    ResourceClosedError,
    DatabaseError,
    DBAPIError,
    SQLAlchemyError,
)
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import logging

logger: logging.Logger = logging.getLogger(__name__)


def add_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers for the FastAPI application.

    This function maps specific exception types (Database, Validation, Timeout)
    to standardized JSON responses. It ensures that internal server errors
    are logged but not exposed to the client, while validation errors provide
    actionable feedback.

    Args:
        app (FastAPI): The main application instance to attach handlers to.
    """

    # --- DATA & VALUE ERRORS ---
    @app.exception_handler(DataError)
    @app.exception_handler(IdentifierError)
    async def data_value_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handles errors where the data value is invalid for the column type
        (e.g., numeric overflow or string too long).
        """
        logger.error(f"Database Data Error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "The data provided is incompatible with the database constraints.",
                "hint": "Check for string length limits or numeric ranges.",
            },
        )

    # --- EXECUTION STATE ERRORS ---
    @app.exception_handler(MultipleResultsFound)
    @app.exception_handler(NoResultFound)
    @app.exception_handler(ResourceClosedError)
    @app.exception_handler(IllegalStateChangeError)
    async def execution_state_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handles logic errors during query execution, like finding multiple
        results when only one was expected.
        """
        logger.error(f"Execution State Error: {exc}")

        # Determine status code based on exception type
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if isinstance(exc, NoResultFound):
            status_code = status.HTTP_404_NOT_FOUND

        return JSONResponse(
            status_code=status_code,
            content={
                "detail": "A database execution error occurred.",
                "type": type(exc).__name__,
            },
        )
    

    # --- SPECIFIC DATABASE ERRORS ---

    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(
        request: Request,
        exc: IntegrityError,
    ) -> JSONResponse:
        logger.error(f"Database Integrity Error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "Data conflict: (likely email or username) already exists."
            },
        )

    @app.exception_handler(NoReferencedTableError)
    async def no_referenced_table_handler(
        request: Request,
        exc: NoReferencedTableError,
    ) -> JSONResponse:
        # We log this as CRITICAL because it means the database schema is broken/missing
        logger.critical(f"Schema Error: {exc}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Database schema error: A required table does not exist.",
                "technical_context": "Run migrations (Alembic) to ensure the schema is up to date.",
            },
        )

    @app.exception_handler(ProgrammingError)
    async def programming_error_handler(
        request: Request,
        exc: ProgrammingError,
    ) -> JSONResponse:
        # Get the raw error from the asyncpg driver
        # PostgreSQL Error Code 42P01 = undefined_table
        raw_error = getattr(exc.orig, "sqlstate", None)

        if raw_error == "42P01":
            logger.critical("CRITICAL: Database table missing (42P01).")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Database schema error: A required table does not exist.",
                    "solution": "Run 'alembic upgrade head' to create the missing tables.",
                },
            )
        
        if raw_error == "42703":
            logger.critical("CRITICAL: Database column mismatch (42703).")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Database schema error: A column referenced in the code does not exist in the database.",
                    "solution": "Generate and run a new migration: 'alembic revision --autogenerate' followed by 'alembic upgrade head'.",
                },
            )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": f"Internal Database Command Failed: raw_error: {raw_error}"}
        )


    # --- CONNECTION & POOL ERRORS ---
    @app.exception_handler(DisconnectionError)
    @app.exception_handler(InvalidatePoolError)
    @app.exception_handler(InterfaceError)
    @app.exception_handler(DBAPIError)
    async def connection_management_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Handles low-level driver and connection pooling issues.
        """
        logger.critical(f"Database Connection/Pool Error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "Database communication failure. The service is temporarily unavailable.",
                "retry": True,
            },
        )

    # --- STATEMENT & COMPILATION ERRORS ---
    @app.exception_handler(StatementError)
    @app.exception_handler(ObjectNotExecutableError)
    @app.exception_handler(UnboundExecutionError)
    @app.exception_handler(NotSupportedError)
    async def statement_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handles errors related to the SQL statement itself, such as passing
        the wrong types to a query or attempting to execute a non-executable object.
        """
        logger.error(f"SQL Statement Error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "The database received an invalid command.",
                "type": type(exc).__name__,
            },
        )

    # --- TRANSACTION & SESSION ERRORS ---
    @app.exception_handler(PendingRollbackError)
    @app.exception_handler(InvalidRequestError)
    @app.exception_handler(MissingGreenlet)
    async def session_lifecycle_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Handles session state errors. In async environments, MissingGreenlet
        usually means you're trying to use a sync driver where an async one is required.
        """
        logger.critical(f"Database Session Error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "A database session error occurred. The transaction may have failed.",
                "hint": "The session requires a rollback or was used incorrectly across threads/tasks.",
            },
        )

    # --- ENGINE & METADATA ERRORS ---
    @app.exception_handler(InternalError)
    @app.exception_handler(DatabaseError)
    @app.exception_handler(NoInspectionAvailable)
    @app.exception_handler(UnreflectableTableError)
    async def engine_metadata_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handles internal database engine failures or issues with
        SQLAlchemy's inspection API.
        """
        logger.critical(f"Database Engine Internal Error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "The database engine encountered an internal failure.",
                "type": type(exc).__name__,
            },
        )

    # --- RELATIONSHIP LINKAGE ERRORS ---
    @app.exception_handler(NoForeignKeysError)
    @app.exception_handler(NoReferencedColumnError)
    @app.exception_handler(NoReferenceError)
    async def relationship_linkage_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Handles errors where foreign key relationships or referenced
        columns are missing or improperly defined.
        """
        logger.error(f"Database Relationship Linkage Error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Database relationship configuration error.",
                "hint": "A foreign key or referenced column is missing from the schema.",
            },
        )

    # --- INTERNAL LOGIC & CODING ERRORS ---
    @app.exception_handler(ArgumentError)
    @app.exception_handler(AwaitRequired)
    @app.exception_handler(UnsupportedCompilationError)
    @app.exception_handler(CompileError)
    async def internal_logic_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handles errors caused by incorrect SQLAlchemy usage (e.g. forgot 'await'
        on an async call, or passed bad arguments to a query).
        """
        logger.error(f"SQLAlchemy Logic Error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "A database logic error occurred.",
                "type": type(exc).__name__,
            },
        )

    # --- COMPLEX SCHEMA & RELATIONSHIP ERRORS ---
    @app.exception_handler(AmbiguousForeignKeysError)
    @app.exception_handler(CircularDependencyError)
    @app.exception_handler(ConstraintColumnNotFoundError)
    @app.exception_handler(DuplicateColumnError)
    async def schema_logic_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handles errors in model relationships, such as circular references
        or multiple foreign keys without specific 'foreign_keys' definitions.
        """
        logger.critical(f"Database Relationship Error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Database schema relationship error.",
                "hint": "Check your model relationships and foreign key definitions.",
            },
        )

    # --- SCHEMA REFLECTION ERRORS ---

    @app.exception_handler(NoSuchTableError)
    @app.exception_handler(NoSuchColumnError)
    async def schema_mismatch_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handles errors where the code tries to access a table or column
        that does not exist in the database (common in reflection).
        """
        logger.critical(f"Schema Mismatch: {exc}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Database structure mismatch.",
                "technical_context": "The application is trying to access a table or column that does not exist.",
            },
        )

    # --- CONFIGURATION ERRORS ---

    @app.exception_handler(NoSuchModuleError)
    async def module_error_handler(
        request: Request, exc: NoSuchModuleError
    ) -> JSONResponse:
        """
        Handles missing database drivers (e.g., trying to use asyncpg without installing it).
        """
        logger.critical(f"Dependency Error: {exc}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Server configuration error: A required database driver is missing.",
                "hint": "Check if 'asyncpg' or 'psycopg2' is installed in the environment.",
            },
        )
    

    # --- GENERAL DATABASE ERROR (Parent) ---


    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request,
        exc: SQLAlchemyError,
    ) -> JSONResponse:
        logger.error(f"General Database Error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "A database error occurred. Please try again later."},
        )



    @app.exception_handler(OperationalError)
    async def operational_handler(
        request: Request,
        exc: OperationalError,
    ) -> JSONResponse:
        logger.critical(f"DB Connection Error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "Database connection failed. Please check if the DB is running."
            },
        )


    # --- VALIDATION & TIMEOUT ---

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        # Flattens the complex Pydantic errors
        errors = {err["loc"][-1]: err["msg"] for err in exc.errors()}
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": "Validation Error", "errors": errors},
        )

    @app.exception_handler(TimeoutError)
    async def timeout_handler(
        request: Request,
        exc: TimeoutError,
    ) -> JSONResponse:
        logger.error(f"Error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"detail": "The database took too long to respond."},
        )

    # --- UNIVERSAL CATCH-ALL (The Ultimate Parent) ---

    @app.exception_handler(Exception)
    async def universal_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.error(f"Uncaught Exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "A critical server error occurred."},
        )
