from tortoise.contrib.pydantic import pydantic_model_creator
from app.modules.todo.model import Todo


TodoPydantic = pydantic_model_creator(Todo, name="Todo")
TodoIn = pydantic_model_creator(Todo, name="TodoIn", exclude_readonly=True)
