from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SyncUserRequest(BaseModel):
    supabase_id: str
    email: str
    full_name: str
    avatar_url: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    supabase_id: str
    email: str
    full_name: str
    avatar_url: str | None
    role: str
