from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from db.database import Base



class DbComment(Base):
    __tablename__: str = "comment"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        comment="Unique identifier for the comment (Auto-incrementing PK).",
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=False,
        unique=False,
        nullable=False,
        index=True,
        comment="Unique identifier for the user of the comment",
    )
    post_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=False,
        unique=False,
        nullable=False,
        index=True,
        comment="Unique identifier for the post where the comment is written",
    )
    text: Mapped[str] = mapped_column(
        String(256),
        primary_key=False,
        unique=False,
        nullable=True,
        index=False,
        comment="string of 256 lenght max.",
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Timestamp of when the comment was created.",
    )
