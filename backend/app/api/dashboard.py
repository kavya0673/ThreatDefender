from fastapi import APIRouter

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats():
    return {
        "risk_score": 74,
        "endpoints_discovered": 1254,
        "total_vulnerabilities": 89,
        "critical_count": 5,
        "high_count": 12,
        "medium_count": 34,
        "low_count": 38,
        "scan_history": [
            {"date": "2026-05-01", "count": 12},
            {"date": "2026-05-02", "count": 15},
            {"date": "2026-05-03", "count": 8},
            {"date": "2026-05-04", "count": 22},
            {"date": "2026-05-05", "count": 18}
        ]
    }
