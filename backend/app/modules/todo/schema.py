from tortoise.contrib.pydantic import pydantic_model_creator
from app.modules.todo.model import Todo


todo_base_schema = pydantic_model_creator(Todo, name="Todo")
