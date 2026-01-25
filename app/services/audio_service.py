import asyncio
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

        # Mock results
        job.stems = {
            "vocals": f"stems/{job_id}/vocals.wav",
            "drums": f"stems/{job_id}/drums.wav",
            "bass": f"stems/{job_id}/bass.wav",
            "other": f"stems/{job_id}/other.wav",
            "backing_vocals": f"stems/{job_id}/backing.wav"
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
