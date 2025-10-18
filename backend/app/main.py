import asyncio
import logging

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

from tortoise import Tortoise
from tortoise.contrib.fastapi import RegisterTortoise, tortoise_exception_handlers

from app.core.db import TORTOISE_ORM, get_db_conf_test

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


@asynccontextmanager
async def lifespan_test(app: FastAPI):
    # Use RegisterTortoise as context manager for test lifecycle
    async with RegisterTortoise(
        app=app,
        config=get_db_conf_test(),
        generate_schemas=True,
        _create_db=True,
    ):
        yield
    # ensure test DB dropped after test lifecycle
    try:
        await Tortoise._drop_databases()
    except Exception:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Redis connect (non-blocking; log failures and continue)
    try:
        redis_conn = get_redis_connection()
        app.state.redis = redis_conn
        logger.info("Redis connection established")
    except Exception as e:
        logger.exception(f"Redis connection failed: {e}")

    # logger.info("Initiating scheduler")
    # await init_scheduler()

    try:
        if getattr(app.state, "testing", None):
            async with lifespan_test(app):
                yield
            # after test context manager exits we return
            return

        # initialize Tortoise only if not initialized already
        if not getattr(Tortoise, "apps", None):
            logger.debug("Tortoise starting..")
            await Tortoise.init(TORTOISE_ORM)
            logger.debug("Tortoise intialized")
        else:
            logger.debug("Tortoise already initialized")

        # generate schemas with timeout to avoid indefinite hang
        if settings.GENERATE_SCHEMAS:
            timeout = getattr(settings, "GENERATE_SCHEMAS_TIMEOUT", 10)
            try:
                logger.info("Start generating schemas")
                await Tortoise.generate_schemas()
                logger.info("Tortoise schemas generated")
            except asyncio.TimeoutError:
                logger.warning(
                    f"Tortoise.generate_schemas() timed out after {timeout}s. Continuing without blocking startup."
                )
            except Exception:
                logger.exception(
                    "Tortoise.generate_schemas() failed but will not block startup"
                )

        logger.info("Tortoise ORM connected")
    except Exception as e:
        logger.exception(f"Tortoise ORM init failed: {e}")

    # normal app runtime
    yield

    # teardown
    if hasattr(app.state, "redis"):
        try:
            await app.state.redis.close()
            logger.info("Redis connection closed")
        except Exception:
            logger.exception("Error closing Redis connection")

    try:
        await Tortoise.close_connections()
        logger.info("Tortoise ORM connection closed")
    except Exception as e:
        logger.exception(f"Tortoise ORM shutdown failed: {e}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    generate_unique_id_function=custom_generate_unique_id,
    default_response_class=ORJSONResponse,
    exception_handlers={
        **tortoise_exception_handlers(),
    },
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


@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": f"Welcome to {settings.PROJECT_NAME} API!"}
