from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# from app.services.product_cleanup import cleanup_outdated_products
# from app.worker.token import refresh_sa_token

scheduler = AsyncIOScheduler()


def init_scheduler():
    # scheduler.add_job(
    #     validate_user,
    #     trigger=IntervalTrigger(hours=6),
    #     id="validate_user",
    #     name="Validate User",
    #     replace_existing=True,
    # )

    scheduler.start()
