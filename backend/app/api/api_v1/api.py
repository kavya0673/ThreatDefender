from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, scans, reports, dashboard

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(scans.router, prefix="/scans", tags=["Scans"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
