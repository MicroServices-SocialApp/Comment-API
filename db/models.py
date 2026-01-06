from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from db.database import Base



class DbAbc(Base):
    __tablename__: str = "user"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        comment="Unique identifier for the user (Auto-incrementing PK).",
    )
    abc: Mapped[str] = mapped_column(
        String(40),
        unique=True,
        nullable=False,
        comment="Unique display name. Used for public profile URLs and mentions.",
    )
    hashed_password: Mapped[str] = mapped_column(
        String,
        comment="Werkzeug hash (scrypt:32768:8:1). Use check_password_hash to verify.",
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Timestamp of when the account was created.",
    )
