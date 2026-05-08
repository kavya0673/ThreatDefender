from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
import enum

Base = declarative_base()

class Severity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String, default="user") # user, admin

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    target_url = Column(String, index=True)
    status = Column(String, default="pending") # pending, running, completed, failed
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    risk_score = Column(Integer, default=0)
    endpoints_checked = Column(Integer, default=0)
    endpoints_total = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"))
    engine_logs = Column(JSON, default=list)
    
    findings = relationship("Finding", back_populates="scan")

class Finding(Base):
    __tablename__ = "findings"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    type = Column(String) # SQLi, XSS, etc.
    severity = Column(String)
    url = Column(String)
    parameter = Column(String, nullable=True)
    payload = Column(Text, nullable=True)
    description = Column(Text)
    remediation = Column(Text)
    evidence = Column(JSON, nullable=True) # Proof of concept details
    ai_analysis = Column(Text, nullable=True)
    
    scan = relationship("Scan", back_populates="findings")

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="pending") # pending, completed, failed
    
    scan = relationship("Scan")
