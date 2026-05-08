from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.models.models import User, Report, Scan, Finding
from app.services.reporting import ReportingService
import os

router = APIRouter()

@router.post("/{scan_id}/generate")
async def trigger_report_generation(
    scan_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    report = Report(scan_id=scan_id, status="pending")
    db.add(report)
    db.commit()
    db.refresh(report)

    try:
        findings = db.query(Finding).filter(Finding.scan_id == scan.id).all()
        file_path = ReportingService().generate_pdf(scan, findings)
        report.file_path = file_path
        report.status = "completed"
        db.commit()
        db.refresh(report)
    except Exception as exc:
        report.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Report generation failed: {exc}") from exc

    return {
        "report_id": report.id,
        "status": report.status,
        "download_url": f"/api/v1/reports/download/{report.id}",
    }

@router.get("/history")
async def get_report_history(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    reports = db.query(Report).join(Scan).filter(Scan.user_id == current_user.id).all()
    return reports

@router.get("/download/{report_id}")
async def download_report(
    report_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    report = db.query(Report).join(Scan).filter(
        Report.id == report_id,
        Scan.user_id == current_user.id,
    ).first()
    if not report or report.status != "completed":
        raise HTTPException(status_code=404, detail="Report not ready or not found")
    
    if not os.path.exists(report.file_path):
         raise HTTPException(status_code=404, detail="Physical report file not found on server")
         
    return FileResponse(report.file_path, filename=os.path.basename(report.file_path))
