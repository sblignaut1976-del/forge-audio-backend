from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import asyncio
import os
from ..database import get_db
from ..models.job import Job
from ..services.chord_service import chord_service

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.get("/{job_id}")
async def get_job_status(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {
        "id": job.id,
        "filename": job.filename,
        "status": job.status,
        "progress": job.progress,
        "stems": job.stems,
        "error": job.error_message
    }

@router.post("/{job_id}/detect-chords")
async def detect_chords(job_id: int, stem: str = None, db: Session = Depends(get_db)):
    print(f"[API] Triggering chord detection for job {job_id}, target stem: {stem or 'default'}")
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        print(f"[API] Job {job_id} not found")
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Chord detection works best on melodic stems (Piano or Other)
    stem_path = None
    melodic_key = None
    
    if job.stems:
        # If a specific stem is requested, search for it
        if stem:
            # Flexible matching for stem names
            for key in job.stems.keys():
                if stem.lower() in key.lower():
                    melodic_key = key
                    path = job.stems.get(key)
                    # Construct absolute path
                    import tempfile
                    base_temp_dir = os.path.join(tempfile.gettempdir(), "forge_audio")
                    stem_path = os.path.join(base_temp_dir, path.lstrip('/'))
                    print(f"[API] Targeted specific stem: {key} at {stem_path}")
                    break
        
        # Fallback to default melodic stems if no specific stem found/requested
        if not stem_path:
            for key in ["Piano", "Other Instruments", "Other"]:
                path = job.stems.get(key)
                if path:
                    melodic_key = key
                    import tempfile
                    base_temp_dir = os.path.join(tempfile.gettempdir(), "forge_audio")
                    stem_path = os.path.join(base_temp_dir, path.lstrip('/'))
                    print(f"[API] Found default melodic stem: {key} at {stem_path}")
                    break

    if not stem_path:
        print(f"[API] No suitable stem found for analysis. Stems available: {job.stems}")
        raise HTTPException(status_code=400, detail="No suitable stem found for chord analysis. Please ensure the track finished processing.")

    if not os.path.exists(stem_path):
        print(f"[API] Physical file not found at path: {stem_path}")
        raise HTTPException(status_code=400, detail=f"File not found on disk. Tried: {stem_path}")

    try:
        print(f"[API] Starting analysis on {melodic_key}...")
        # Run blocking chord detection in a separate thread to keep event loop free
        chords = await asyncio.to_thread(chord_service.detect_chords, stem_path)
        
        # job.chords = chords # Column does not exist in production
        # db.commit()
        print(f"[API] Analysis successful. {len(chords)} chords saved (in-memory only).")
        return {"status": "success", "chords": chords, "analyzed_stem": melodic_key}
    except Exception as e:
        print(f"[API] Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chord detection failed: {str(e)}")
