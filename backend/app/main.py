"""BLUECHAIN: AI-Powered Ocean Behaviour and Impact Prediction System.
Main FastAPI application entry point with CORS, APScheduler, OpenAPI documentation, and auto-seeding.
"""
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import engine, Base, SessionLocal
from backend.app.db.models import Observation
from backend.app.api.router import api_router
from backend.app.api.ingest import run_full_sync

scheduler = BackgroundScheduler()


def scheduled_sync_job():
    logger.info("Executing scheduled oceanic data ingestion sync...")
    db = SessionLocal()
    try:
        run_full_sync(db)
    except Exception as e:
        logger.error(f"Error in scheduled sync job: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist
    logger.info("Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)

    # Initial data seed if empty
    db = SessionLocal()
    try:
        count = db.query(Observation).count()
        if count == 0 and settings.USE_SAMPLE_DATA:
            logger.info("Database is empty. Ingesting initial baseline sample data...")
            run_full_sync(db)
    except Exception as e:
        logger.error(f"Initial seed error: {e}")
    finally:
        db.close()

    # Start background scheduler for periodic ingestion
    try:
        scheduler.add_job(scheduled_sync_job, "interval", hours=6, id="ocean_ingest_sync")
        scheduler.start()
        logger.info("APScheduler initialized: Ingestion running every 6 hours.")
    except Exception as e:
        logger.warning(f"Scheduler could not start: {e}")

    yield

    # Shutdown
    if scheduler.running:
        scheduler.shutdown()
    logger.info("BLUECHAIN backend shutdown completed.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Full-Stack Ocean Impact Prediction Engine (OIPE) monitoring and predicting marine events: "
        "Marine Heatwaves (Hobday criteria), Offshore Subduction Quakes & Tsunamis, "
        "Tropical Cyclones, Harmful Algal Blooms, Arctic/Antarctic Sea Ice Loss, "
        "and 72-Hour Lagrangian Oil Spill Drift Simulation."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local Vite dev server and external clients
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)


@app.get("/api/health", tags=["System Health"])
def health_check():
    """System health check endpoint verifying database connectivity and engine state."""
    db = SessionLocal()
    db_status = "healthy"
    try:
        db.execute(Base.metadata.tables["observations"].select().limit(1))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    finally:
        db.close()

    return {
        "status": "healthy",
        "app_env": settings.APP_ENV,
        "database": db_status,
        "sample_data_mode": settings.USE_SAMPLE_DATA,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
