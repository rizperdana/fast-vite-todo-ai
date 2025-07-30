import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app.modules.routers import routers
from app.core.config import Settings

# from tortoise import Tortoise, generate_config
# from tortoise.contrib.fastapi import RegisterTortoise, tortoise_exception_handlers


# @asynccontextmanager
# async def lifespan_test(app: FastAPI) -> AsyncGenerator[None, None]:
#     config = generate_config(
#         os.getenv("TORTOISE_TEST_DB", "sqlite://:memory:"),
#         app_modules={"models": ["models"]},
#         testing=True,
#         connection_label="models",
#     )
#     async with RegisterTortoise(
#         app=app,
#         config=config,
#         generate_schemas=True,
#         _create_db=True,
#     ):
#         # db connected
#         yield
#         # app teardown
#     # db connections closed
#     await Tortoise._drop_databases()


# @asynccontextmanager
# async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
#     if getattr(app.state, "testing", None):
#         async with lifespan_test(app) as _:
#             yield
#     else:
#         # app startup
#         async with register_orm(app):
#             # db connected
#             yield
#             # app teardown
#         # db connections closed

app = FastAPI()

origins = [
    "http://localhost:5173",
    "localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers, prefix="/api/v1")

@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to todo list API!"}
