from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class TodoCreate(BaseModel):
    id: int = Field(description="Unique identifier for the todo item", example=1)
    item: str = Field(min_length=1, max_length=200, description="Todo item description", example="Buy groceries")
    priority: Optional[str] = Field(None, description="Priority level", example="high")

    class Config:
        # This enables better documentation in FastAPI
        schema_extra = {
            "example": {
                "id": 1,
                "item": "Complete FastAPI tutorial",
                "priority": "medium"
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
