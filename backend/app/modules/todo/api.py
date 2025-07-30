from typing import List
from fastapi import APIRouter

from app.modules.todo.schema import TodoResponse

todos = [
    {
        "id": 1,
        "item": "Read a book",
        "priority": 0,
    },
    {
        "id": 2,
        "item": "Code project AZ",
        "priority": 1,
    }
]

api = APIRouter()

@api.get("/todo", response_model=List[TodoResponse])
async def get_todos() -> dict:
    return { "data": todos }


@api.post("/todo")
async def add_todo(todo: dict) -> dict:
    for t in todos:
        if todo["id"] == t["id"]:
            raise Exception("ID must unique")

        if todo["item"].lower().strip() == t["item"].lower().strip():
            raise Exception("Item cannot be the same")

    todos.append(todo)
    return {"data": {"Todo Added"}}


@api.put("/todo/{id}")
async def update_todo(id: int, body: dict)  -> dict:
    for todo in todos:
        if int(todo["id"]) == id:
            todo["item"] = body["item"]
            return {
                "data": f"Todo with {id} has been updated"
            }

    return {
        "data": f"Todo with id {id} not found"
    }


@api.delete("/todo/{id}")
async def delete_todo(id: int) -> dict:
    for todo in todos:
        if int(todo["id"]) == id:
            todos.remove(todo)
            return {
                "data": f"Todo with id {id} has been removed."
            }

    return {
        "data": f"Todo with id {id} not found"
    }
