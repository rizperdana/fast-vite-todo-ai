from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore

from app.core.config import settings as s

# from app.services.product_cleanup import cleanup_outdated_products
# from app.worker.token import refresh_sa_token

jobstores = {
    "default": RedisJobStore(
        host=s.REDIS_HOST,
        port=s.REDIS_PORT,
        ssl=s.REDIS_USE_SSL,  # important
    )
}

scheduler = AsyncIOScheduler(jobstores=jobstores)


def init_scheduler():
    # scheduler.add_job(
    #     validate_user,
    #     trigger=IntervalTrigger(hours=6),
    #     id="validate_user",
    #     name="Validate User",
    #     replace_existing=True,
    # )

    scheduler.start()
