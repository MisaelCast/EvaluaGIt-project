from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    requirements: list | dict | None = None
    due_date: datetime | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    requirements: list | dict | None = None
    due_date: datetime | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    professor_id: UUID
    name: str
    description: str | None
    requirements: list | dict | None
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime
