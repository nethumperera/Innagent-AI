# ════════════════════════════════════════════════════════════════
# InnAgent AI — Scheduler Service
# APScheduler daily cron jobs for automated agent runs
# ════════════════════════════════════════════════════════════════

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.utils.logger import get_logger

logger = get_logger("scheduler")

scheduler = AsyncIOScheduler()


async def daily_pricing_check():
    """Run pricing agent for all active hotels at 6:00 AM IST."""
    from backend.database import get_all_hotels
    from backend.agents.orchestrator import run_orchestrator

    logger.info("Starting daily pricing check for all hotels")
    try:
        hotels = get_all_hotels(active_only=True)
        for hotel in hotels:
            try:
                result = await run_orchestrator(
                    task="daily_pricing_check",
                    hotel_id=hotel["id"],
                    context={"trigger": "scheduled", "job": "daily_pricing"},
                )
                logger.info(f"Pricing check completed for {hotel['name']}: {result.get('action_taken', 'done')}")
            except Exception as e:
                logger.error(f"Pricing check failed for {hotel['name']}: {e}")
    except Exception as e:
        logger.error(f"Daily pricing check job failed: {e}")


async def daily_review_scan():
    """Run review agent for all active hotels at 9:00 AM IST."""
    from backend.database import get_all_hotels
    from backend.agents.orchestrator import run_orchestrator

    logger.info("Starting daily review scan for all hotels")
    try:
        hotels = get_all_hotels(active_only=True)
        for hotel in hotels:
            try:
                result = await run_orchestrator(
                    task="daily_review_scan",
                    hotel_id=hotel["id"],
                    context={"trigger": "scheduled", "job": "daily_reviews"},
                )
                logger.info(f"Review scan completed for {hotel['name']}: {result.get('action_taken', 'done')}")
            except Exception as e:
                logger.error(f"Review scan failed for {hotel['name']}: {e}")
    except Exception as e:
        logger.error(f"Daily review scan job failed: {e}")


async def daily_housekeeping_tasks():
    """Generate housekeeping task lists at 7:00 AM IST."""
    from backend.database import get_all_hotels
    from backend.agents.orchestrator import run_orchestrator

    logger.info("Starting daily housekeeping task generation")
    try:
        hotels = get_all_hotels(active_only=True)
        for hotel in hotels:
            try:
                result = await run_orchestrator(
                    task="daily_housekeeping_tasks",
                    hotel_id=hotel["id"],
                    context={"trigger": "scheduled", "job": "daily_operations"},
                )
                logger.info(f"Housekeeping tasks generated for {hotel['name']}: {result.get('action_taken', 'done')}")
            except Exception as e:
                logger.error(f"Housekeeping task generation failed for {hotel['name']}: {e}")
    except Exception as e:
        logger.error(f"Daily housekeeping job failed: {e}")


def start_scheduler():
    """Configure and start the APScheduler with daily cron jobs."""
    # 6:00 AM IST = 00:30 UTC
    scheduler.add_job(
        daily_pricing_check,
        CronTrigger(hour=0, minute=30, timezone="UTC"),
        id="daily_pricing",
        name="Daily Pricing Check",
        replace_existing=True,
    )

    # 9:00 AM IST = 03:30 UTC
    scheduler.add_job(
        daily_review_scan,
        CronTrigger(hour=3, minute=30, timezone="UTC"),
        id="daily_reviews",
        name="Daily Review Scan",
        replace_existing=True,
    )

    # 7:00 AM IST = 01:30 UTC
    scheduler.add_job(
        daily_housekeeping_tasks,
        CronTrigger(hour=1, minute=30, timezone="UTC"),
        id="daily_operations",
        name="Daily Housekeeping Tasks",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with 3 daily cron jobs")


def stop_scheduler():
    """Shutdown the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
