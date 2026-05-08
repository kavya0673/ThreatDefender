from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
import httpx
import asyncio
import time
from urllib.parse import urlparse
from typing import Any, List
from sqlalchemy.orm import Session

from app.api import deps
from app.models.models import User, Scan
from app.scanner.engine import ScannerEngine

router = APIRouter()

class ScanCreate(BaseModel):
    url: str

# Helper functions (omitted for brevity in this foundational setup, 
# but they would be imported from a separate scanning service)
# For now, I'll include the compute_risk_score since it's used below.

def compute_risk_score(findings: list) -> int:
    if not findings:
        return 0
    weights = {"critical": 10, "high": 7, "medium": 4, "low": 2, "info": 1}
    total = sum(weights.get(f["severity"], 0) for f in findings)
    max_possible = len(findings) * 10
    return min(int((total / max_possible) * 100), 99) if max_possible else 0

def cvss_for_severity(severity: str) -> float:
    return {
        "critical": 9.5,
        "high": 7.5,
        "medium": 5.0,
        "low": 2.5,
        "info": 0.0,
    }.get((severity or "").lower(), 0.0)

def normalize_scan_url(url: str) -> str:
    clean_url = url.strip()
    if not clean_url:
        raise HTTPException(status_code=400, detail="URL is required")
    if not clean_url.startswith(("http://", "https://")):
        clean_url = "https://" + clean_url
    parsed = urlparse(clean_url)
    if not parsed.netloc:
        raise HTTPException(status_code=400, detail="Please enter a valid target URL")
    return clean_url.rstrip("/")

@router.post("/start", response_model=Any)
async def start_scan(
    scan_in: ScanCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Start a full recursive website scan as a background task.
    """
    # 1. Create scan entry in DB
    scan = Scan(
        target_url=normalize_scan_url(scan_in.url),
        user_id=current_user.id,
        status="pending"
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    # 2. Use FastAPI BackgroundTasks directly (Redis/Celery not available locally)
    async def run_scan_local(scan_id: int):
        from app.db.session import SessionLocal
        import logging
        log = logging.getLogger(__name__)
        db_local = SessionLocal()
        try:
            engine = ScannerEngine(db_local, scan_id)
            await engine.run()
        except Exception as ex:
            log.error(f"Background scan {scan_id} failed: {ex}")
        finally:
            db_local.close()

    background_tasks.add_task(run_scan_local, scan.id)

    return {
        "scan_id": scan.id,
        "status": "pending",
        "message": "Scan started successfully."
    }

@router.get("/{scan_id}", response_model=Any)
async def get_scan_status(
    scan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    findings_data = [
        {
            "id": f.id,
            "type": f.type,
            "severity": f.severity,
            "url": f.url,
            "parameter": f.parameter,
            "description": f.description,
            "remediation": f.remediation,
            "ai_analysis": f.ai_analysis,
            "risk_score": cvss_for_severity(f.severity)
        }
        for f in scan.findings
    ]

    return {
        "id": scan.id,
        "target_url": scan.target_url,
        "status": scan.status,
        "risk_score": scan.risk_score,
        "endpoints_checked": getattr(scan, "endpoints_checked", 0) or 0,
        "endpoints_total": getattr(scan, "endpoints_total", 0) or 0,
        "findings_count": len(scan.findings),
        "findings": findings_data,
        "engine_logs": scan.engine_logs
    }

@router.get("/{scan_id}/findings", response_model=Any)
async def get_scan_findings(
    scan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return [
        {
            "id": f.id,
            "type": f.type,
            "severity": f.severity,
            "url": f.url,
            "parameter": f.parameter,
            "description": f.description,
            "remediation": f.remediation,
            "ai_analysis": f.ai_analysis,
            "risk_score": cvss_for_severity(f.severity)
        }
        for f in scan.findings
    ]
