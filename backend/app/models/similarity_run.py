import uuid

from sqlalchemy import Column, DateTime, ForeignKey, JSON, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class SimilarityRun(Base):
    __tablename__ = "similarity_runs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
    )
    status = Column(String, nullable=False, default="PENDING")
    result_json = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
