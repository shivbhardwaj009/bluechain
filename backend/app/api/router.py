from fastapi import APIRouter
from backend.app.api.events import router as events_router
from backend.app.api.parameters import router as parameters_router
from backend.app.api.forecast import router as forecast_router
from backend.app.api.risk import router as risk_router
from backend.app.api.spill import router as spill_router
from backend.app.api.ice import router as ice_router
from backend.app.api.ingest import router as ingest_router

api_router = APIRouter(prefix="/api")

api_router.include_router(events_router)
api_router.include_router(parameters_router)
api_router.include_router(forecast_router)
api_router.include_router(risk_router)
api_router.include_router(spill_router)
api_router.include_router(ice_router)
api_router.include_router(ingest_router)
