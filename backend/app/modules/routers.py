from fastapi import APIRouter

from app.modules.todo.api import api as todo_api

routers = APIRouter()
routers.include_router(todo_api, tags=["todo"])
