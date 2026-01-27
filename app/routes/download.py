from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.job import Job
import os
import zipstream
import io

router = APIRouter(prefix="/api/download", tags=["download"])

@router.get("/{job_id}/all")
async def export_all_stems(job_id: int, stems: str = None, db: Session = Depends(get_db)):
    from urllib.parse import unquote
    requested_stems = None
    if stems:
        requested_stems = [unquote(s.strip()) for s in stems.split(',')]
        print(f"[DOWNLOAD] Filtered ZIP request for Job {job_id}, Stems: {requested_stems}")
    else:
        print(f"[DOWNLOAD] Full ZIP export for Job {job_id}")
        
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or not job.stems:
        raise HTTPException(status_code=404, detail="Stems not found for this job")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    stems_dir = os.path.join(base_dir, "stems", str(job_id))
    
    if not os.path.exists(stems_dir):
        raise HTTPException(status_code=404, detail="Stems directory not found")

    def generator():
        z = zipstream.ZipStream()
        for stem_name, stem_path in job.stems.items():
            # If a filter is provided, skip stems not in the list
            if requested_stems and stem_name not in requested_stems:
                continue
                
            filename = os.path.basename(stem_path)
            abs_path = os.path.join(stems_dir, filename)
            if os.path.exists(abs_path):
                z.add_path(abs_path, arcname=filename)
        
        for chunk in z:
            yield chunk

    response = StreamingResponse(generator(), media_type="application/zip")
    response.headers["Content-Disposition"] = f"attachment; filename=forge_audio_stems_{job_id}.zip"
    return response

@router.get("/{job_id}/{stem_name}")
async def download_stem(job_id: int, stem_name: str, db: Session = Depends(get_db)):
    from urllib.parse import unquote
    # Handle both URL encoding (e.g., %20) and browser behavior
    stem_name = unquote(stem_name)
    print(f"[DOWNLOAD] Individual stem request for Job {job_id}, Stem: {stem_name}")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.stems:
        raise HTTPException(status_code=404, detail="Stems not generated yet")

    if stem_name not in job.stems:
        print(f"[DOWNLOAD] Error: Stem '{stem_name}' not found. Available: {list(job.stems.keys())}")
        raise HTTPException(status_code=404, detail="Stem not found")
    
    stem_path = job.stems[stem_name]
    filename = os.path.basename(stem_path)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, "stems", str(job_id), filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File on disk not found")
        
    return FileResponse(
        path=file_path,
        filename=f"{job.filename.split('.')[0]}_{stem_name.replace(' ', '_')}{os.path.splitext(filename)[1]}",
        media_type="audio/wav"
    )
