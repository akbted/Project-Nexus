from datetime import datetime
from pydantic import BaseModel, Field


class Description(BaseModel):
    format: str
    raw: str
    html: str


class Project(BaseModel):
    id: int
    identifier: str
    name: str
    active: bool
    public: bool

    description: Description | None = None

    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")