import os
import logging
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

# ------------------------------------------------------------------------------------

# This tells SQLAlchemy exactly how to name constraints
convention = {
    "ix": "ix_%(column_0_label)s", # Index
    "uq": "uq_%(table_name)s_%(column_0_name)s", # Unique Constraint
    "ck": "ck_%(table_name)s_%(constraint_name)s", # Check Constraint
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s", # Foreign key
    "pk": "pk_%(table_name)s", # Primary key
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)

# ------------------------------------------------------------------------------------

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# ------------------------------------------------------------------------------------

load_dotenv()
DATABASE_URL: str | None = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("CRITICAL: DATABASE_URL environment variable is required.")

# ------------------------------------------------------------------------------------

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ------------------------------------------------------------------------------------

async def get_async_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()
