from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class WorkPackageDescription(BaseModel):
    format: str
    raw: str
    html: str


class WorkPackage(BaseModel):
    id: int
    subject: str
    description: Optional[WorkPackageDescription] = None
    startDate: Optional[str] = None
    dueDate: Optional[str] = None
    percentageDone: Optional[int] = None
    createdAt: datetime
    updatedAt: datetime
    links: dict = Field(alias="_links") 