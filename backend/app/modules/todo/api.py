from typing import List
from fastapi import APIRouter

from app.modules.todo.schema import todo_base_schema

api = APIRouter()


@api.get("/todo", response_model=List[todo_base_schema])
async def get_todos() -> dict:
    todos = []
    return {"data": todos}


@api.post("/todo")
async def add_todo(todo: dict) -> dict:
    return {"data": {"Todo Added"}}


@api.put("/todo/{id}")
async def update_todo(id: int, body: dict) -> dict:
    return {"data": f"Todo with id {id} not found"}


@api.delete("/todo/{id}")
async def delete_todo(id: int) -> dict:
    return {"data": f"Todo with id {id} not found"}
