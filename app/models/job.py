from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from sqlalchemy.sql import func
from ..database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    stems = Column(JSON, nullable=True)  # Store paths to separated stems: {"vocals": "...", "drums": "...", ...}
    chords = Column(JSON, nullable=True) # Store detected chords: [{"time": 0.0, "chord": "C"}, ...]
    error_message = Column(String, nullable=True)

    def __repr__(self):
        return f"<Job id={self.id} filename={self.filename} status={self.status}>"
