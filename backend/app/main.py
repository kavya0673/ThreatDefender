from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.api_v1.api import api_router
from app.core.config import settings
from app.models.models import Base
from app.db.session import engine
from sqlalchemy import inspect, text
import os
import time
import logging

import sys
print(f"DEBUG: Python Path: {sys.path}")
print(f"DEBUG: Current Directory: {os.getcwd()}")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ThreatDefender")

def ensure_local_schema():
    """Add columns that older local SQLite databases may be missing."""
    if engine.dialect.name != "sqlite":
        return

    expected_columns = {
        "users": {
            "full_name": "VARCHAR",
            "role": "VARCHAR DEFAULT 'user'",
        },
        "scans": {
            "risk_score": "INTEGER DEFAULT 0",
            "endpoints_checked": "INTEGER DEFAULT 0",
            "endpoints_total": "INTEGER DEFAULT 0",
            "engine_logs": "JSON",
        },
        "findings": {
            "payload": "TEXT",
            "evidence": "JSON",
            "ai_analysis": "TEXT",
        },
    }

    inspector = inspect(engine)
    with engine.begin() as conn:
        for table_name, columns in expected_columns.items():
            if not inspector.has_table(table_name):
                continue
            existing = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, column_sql in columns.items():
                if column_name not in existing:
                    logger.info("Adding missing SQLite column %s.%s", table_name, column_name)
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}"))

try:
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    ensure_local_schema()
except Exception as e:
    logger.error(f"Database initialization failed: {e}")

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "time": time.time()}

# Include versioned API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve Frontend Static Files
# Calculate path relative to this file: backend/app/main.py
# Go up 3 levels to reach the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
frontend_path = os.path.join(BASE_DIR, "frontend", "dist")

logger.info(f"Checking frontend path: {frontend_path}")

if os.path.exists(frontend_path):
    logger.info("Frontend dist found. Mounting static files.")
    # Static files (JS/CSS)
    assets_path = os.path.join(frontend_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/")
    async def serve_index():
        try:
            return FileResponse(os.path.join(frontend_path, "index.html"))
        except:
            return {"message": "Server is up, but index.html could not be read"}

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Don't intercept API or Health calls
        if full_path.startswith("api/") or full_path.startswith("health") or full_path.startswith("docs"):
            return None
        
        index_file = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"error": "Index file missing"}
else:
    logger.warning("Frontend dist NOT found. Root will return API info.")
    @app.get("/")
    async def root():
        return {"message": "ThreatDefender API Operational", "frontend": "Not Built"}

if __name__ == "__main__":
    import uvicorn
    # Use 9005 to avoid the deadlocks on 9000/3001
    logger.info("Starting server on port 9005...")
    uvicorn.run(app, host="127.0.0.1", port=9005)
