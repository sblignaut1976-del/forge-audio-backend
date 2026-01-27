import asyncio
import os
import shutil
import random
from sqlalchemy.orm import Session
from ..models.job import Job
from ..database import SessionLocal
from audio_separator.separator import Separator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_audio_job(job_id: int, file_path: str = None):
    db = SessionLocal()
    job = None
    try:
        print(f"[JOB] Starting job {job_id} for file {file_path}")
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            print(f"[JOB] Job {job_id} not found in database!")
            return

        job.status = "processing"
        job.progress = 0.1
        db.commit()

        # Create output directory for this job (absolute path to be safe)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(base_dir, "stems", str(job_id))
        os.makedirs(output_dir, exist_ok=True)

        if file_path and os.path.exists(file_path):
            # Initialize Separator
            # htdemucs is a high-quality 4-stem model (vocals, drums, bass, other)
            separator = Separator(output_dir=output_dir)
            
            # Update progress
            job.progress = 0.2
            db.commit()
            
            print(f"[JOB] Separating job {job_id} Pass 1 (htdemucs_6s)...")
            # Run the blocking separation in a thread pool
            loop = asyncio.get_event_loop()
            
            # Use htdemucs_6s for native 6-stem separation
            separator.load_model('htdemucs_6s.yaml')
            output_files = await loop.run_in_executor(None, separator.separate, file_path)
            
            job.progress = 0.6
            db.commit()
            
            # audio-separator returns list of filenames in output_dir
            stems_result = {}
            vocals_filename = None
            
            # Mapping 6-stem model outputs to clear keys
            for filename in output_files:
                fn_lower = filename.lower()
                if 'vocals' in fn_lower:
                    vocals_filename = filename
                    stems_result['Vocals'] = f"/stems/{job_id}/{filename}"
                elif 'drums' in fn_lower:
                    stems_result['Drums'] = f"/stems/{job_id}/{filename}"
                elif 'bass' in fn_lower:
                    stems_result['Bass'] = f"/stems/{job_id}/{filename}"
                elif 'guitar' in fn_lower:
                    stems_result['Guitar'] = f"/stems/{job_id}/{filename}"
                elif 'piano' in fn_lower:
                    stems_result['Piano'] = f"/stems/{job_id}/{filename}"
                elif 'other' in fn_lower:
                    stems_result['Other_Signal'] = f"/stems/{job_id}/{filename}"
            
            # Pass 2: Split Vocals into Lead and Backing Vocals if we have a vocals track
            if vocals_filename:
                print(f"[JOB] Job {job_id} Pass 2 (Karaoke) - Splitting vocals...")
                vocals_full_path = os.path.join(output_dir, vocals_filename)
                
                # Load specialized Karaoke model
                separator.load_model('UVR_MDXNET_KARA_2.onnx')
                
                job.progress = 0.85
                db.commit()
                
                output_files_kara = await loop.run_in_executor(None, separator.separate, vocals_full_path)
                
                for filename in output_files_kara:
                    fn_lower = filename.lower()
                    if '_(vocals)_uvr_mdxnet_kara_2' in fn_lower:
                        stems_result['Lead Vocals'] = f"/stems/{job_id}/{filename}"
                    elif '_(instrumental)_uvr_mdxnet_kara_2' in fn_lower:
                        stems_result['Backing Vocals'] = f"/stems/{job_id}/{filename}"

            # Final assembly and safety checks
            # If Pass 2 (Vocal splitting) failed, fall back to base Vocals
            if 'Lead Vocals' not in stems_result and 'Vocals' in stems_result:
                stems_result['Lead Vocals'] = stems_result['Vocals']

            # Combine Piano and Other into "Other Instruments" for a cleaner 6-stem view
            # (Users often want Melodic/Synths grouped if they already have Bass and Guitar)
            # Actually, I'll provide Guitar as its own track.
            
            # Provide clear mappings for the dashboard
            final_stems = {
                "Lead Vocals": stems_result.get("Lead Vocals"),
                "Backing Vocals": stems_result.get("Backing Vocals"),
                "Drums": stems_result.get("Drums"),
                "Bass": stems_result.get("Bass"),
                "Guitar": stems_result.get("Guitar"),
                "Other Instruments": stems_result.get("Piano") or stems_result.get("Other_Signal")
            }
            
            # Filter out None values
            job.stems = {k: v for k, v in final_stems.items() if v}
        else:
            job.status = "failed"
            job.error_message = "Input file not found"

        job.status = "completed"
        job.progress = 1.0
        db.commit()
        print(f"[JOB] Job {job_id} completed successfully!")

    except Exception as e:
        error_msg = f"Error during separation: {str(e)}"
        print(f"[JOB] Background task error for job {job_id}: {error_msg}")
        if job:
            try:
                job.status = "failed"
                job.error_message = error_msg
                db.commit()
            except Exception as db_err:
                print(f"[JOB] Failed to update job status to error: {db_err}")
    finally:
        db.close()



