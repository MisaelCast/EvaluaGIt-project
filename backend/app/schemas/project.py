from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    requirements: list | dict | None = None
    due_date: datetime | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("El nombre del proyecto no puede estar vacío")
        return name


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    requirements: list | dict | None = None
    due_date: datetime | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        name = value.strip()
        if not name:
            raise ValueError("El nombre del proyecto no puede estar vacío")
        return name


class JoinProjectRequest(BaseModel):
    join_code: str


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    professor_id: UUID
    name: str
    description: str | None
    requirements: list | dict | None
    due_date: datetime | None
    join_code: str
    created_at: datetime
    updated_at: datetime
