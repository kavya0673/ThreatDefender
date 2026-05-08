from app.tasks.scanner_tasks import celery_app
from app.db.session import SessionLocal
from app.models.models import Scan, Finding, Report
from app.services.reporting import ReportingService
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="generate_report_task")
def generate_report_task(report_id: int):
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return
        
        scan = db.query(Scan).filter(Scan.id == report.scan_id).first()
        findings = db.query(Finding).filter(Finding.scan_id == scan.id).all()
        
        reporting_service = ReportingService()
        file_path = reporting_service.generate_pdf(scan, findings)
        
        report.file_path = file_path
        report.status = "completed"
        db.commit()
        logger.info(f"Report {report_id} generated successfully at {file_path}")
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        if report:
            report.status = "failed"
            db.commit()
    finally:
        db.close()
