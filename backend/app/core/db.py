from tortoise.backends.base.config_generator import generate_config

from app.core.config import settings as s
from app.modules.models import TORTOISE_MODELS

DB_CONFIG = f"postgres://{s.POSTGRES_USER}:{s.POSTGRES_PASSWORD}@{s.POSTGRES_HOST}:{s.POSTGRES_PORT}/{s.POSTGRES_DATABASE}"


def get_db_conf_test():
    return generate_config(
        DB_CONFIG + "_test",
        app_modules={"models": TORTOISE_MODELS},
        testing=True,
        connection_label=s.PROJECT_NAME + "_test",
    )


def get_db_conf():
    return generate_config(
        DB_CONFIG,
        app_modules={"models": TORTOISE_MODELS},
        testing=False,
        connection_label=s.PROJECT_NAME,
    )


TORTOISE_ORM = get_db_conf()
