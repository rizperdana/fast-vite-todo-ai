from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRoute
from fastapi_pagination import add_pagination

from asgi_correlation_id import CorrelationIdMiddleware
from contextlib import asynccontextmanager

from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.modules.routers import routers
from app.core.config import settings
from app.core.redis import get_redis_connection
from app.scheduler import init_scheduler

# from tortoise import Tortoise, generate_config
# from tortoise.contrib.fastapi import RegisterTortoise, tortoise_exception_handlers


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    # Initialize services
    init_scheduler()

    # Initialize Redis connection
    try:
        redis_conn = get_redis_connection()
        await redis_conn.ping()
        app.state.redis = redis_conn
        print("Redis connection established")
    except Exception as e:
        print(f"Redis connection failed: {e}")

    yield

    # Close Redis connection
    if hasattr(app.state, "redis"):
        await app.state.redis.close()
        print("Redis connection closed")


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    openapi_url=(
        f"{settings.API_V1_STR}/openapi.json"
        if settings.ENVIRONMENT != "production"
        else None
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    generate_unique_id_function=custom_generate_unique_id,
    default_response_class=ORJSONResponse,
)
add_pagination(app)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(CorrelationIdMiddleware)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(routers, prefix=settings.API_V1_STR)

# register_tortoise(
#     app,
#     db_url=tortoise_config.db_url,
#     generate_schemas=tortoise_config.generate_schemas,
#     modules=tortoise_config.modules,
# )


@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": f"Welcome to {settings.PROJECT_NAME} API!"}
