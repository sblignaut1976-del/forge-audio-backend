from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.job import Job
from ..services.audio_service import process_audio_job
import os
import shutil
import uuid

router = APIRouter(prefix="/api/upload", tags=["upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@router.post("/")
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Note: In a real app, we'd check file size before reading, 
    # but for this scaffold we'll assume light files for now.
    
    # Create unique filename
    file_id = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")
    
    # Save the file
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Create database entry
    job = Job(
        filename=file.filename,
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Trigger separation process in background
    background_tasks.add_task(process_audio_job, job.id)
    
    return {
        "job_id": job.id,
        "message": "Upload successful, separation task queued.",
        "filename": file.filename
    }
