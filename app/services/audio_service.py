import asyncio
import os
import random
from sqlalchemy.orm import Session
from ..models.job import Job
from ..database import SessionLocal

async def process_audio_job(job_id: int):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return

        job.status = "processing"
        db.commit()

        # Simulate processing steps
        steps = [0.2, 0.4, 0.6, 0.8, 1.0]
        for progress in steps:
            await asyncio.sleep(1.0) # Faster simulation
            job.progress = progress
            db.commit()

        # Mock results - Use absolute URLs for frontend accessibility
        api_url = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("Render_External_URL") or "http://localhost:8000"
        if not api_url.startswith("http"):
            api_url = f"https://{api_url}"
            
        job.stems = {
            "vocals": f"{api_url}/stems/1/vocals.wav",
            "drums": f"{api_url}/stems/1/drums.wav",
            "bass": f"{api_url}/stems/1/bass.wav",
            "other": f"{api_url}/stems/1/other.wav",
            "backing": f"{api_url}/stems/1/backing.wav"
        }
        job.status = "completed"
        db.commit()

    except Exception as e:
        print(f"Background task error: {e}")
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
    finally:
        db.close()
