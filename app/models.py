from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from .database import Base


class Item(Base):

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    blob_name: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    original_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    content_type: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
