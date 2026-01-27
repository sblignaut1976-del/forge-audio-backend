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
    import time
    start = time.time()
    print(f"[UPLOAD] Started at {start}")
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    print(f"[UPLOAD] File extension check: {time.time() - start:.2f}s")
    
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
    print(f"[UPLOAD] Path created: {time.time() - start:.2f}s")
    
    # Save the file
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print(f"[UPLOAD] File saved: {time.time() - start:.2f}s")
        
    # Create database entry
    job = Job(
        filename=file.filename,
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    print(f"[UPLOAD] DB commit: {time.time() - start:.2f}s")
    
    # Trigger separation process in background
    background_tasks.add_task(process_audio_job, job.id, save_path)
    print(f"[UPLOAD] Background task added: {time.time() - start:.2f}s")
    
    return {
        "job_id": job.id,
        "message": "Upload successful, separation task queued.",
        "filename": file.filename
    }

