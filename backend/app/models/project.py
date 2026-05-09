import uuid

from sqlalchemy import Column, DateTime, ForeignKey, JSON, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Project(Base):
    """Modelo de proyecto para la base de datos."""

    __tablename__ = "projects"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    professor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    requirements = Column(JSON, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
