from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class TodoCreate(BaseModel):
    id: int
    item: str
    priority: Optional[str]
    created_at: datetime

    class Config:
        # This enables better documentation in FastAPI
        schema_extra = {
            "example": {
                "id": 1,
                "item": "Complete FastAPI tutorial",
                "priority": "medium",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%s")
            }
        }


class TodoResponse(BaseModel):
    id: int
    item: str
    priority: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class TodoAddResponse(BaseModel):
    message: str
    data: TodoResponse


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
