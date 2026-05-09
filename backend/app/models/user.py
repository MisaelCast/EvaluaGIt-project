import uuid
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class UserRole(str, PyEnum):
    """Roles de usuario soportados en la plataforma."""

    ADMIN = "ADMIN"
    PROFESSOR = "PROFESSOR"
    STUDENT = "STUDENT"


class User(Base):
    """Modelo de usuario para la base de datos."""

    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    supabase_id = Column(
        String,
        unique=True,
        nullable=False,
    )
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    role = Column(
        Enum(UserRole, name="userrole"),
        nullable=False,
    )
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
