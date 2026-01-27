from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Forge Audio API",
    description="Stem separation API for Forge Audio",
    version="1.0.0"
)

# Create directories if they don't exist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "..", "uploads")
STEMS_DIR = os.path.join(BASE_DIR, "..", "stems")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(STEMS_DIR, exist_ok=True)

# Serve static files for audio stems
app.mount("/stems", StaticFiles(directory=STEMS_DIR), name="stems")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

from .routes import upload, jobs, download

# Configure CORS
raw_origins = os.getenv("CORS_ORIGINS", "*")
if "•" in raw_origins or not raw_origins.strip():
    origins = ["*"]
else:
    origins = [
        origin.strip() 
        for origin in raw_origins.split(",") 
        if origin.strip()
    ]
    if "*" in raw_origins:
        origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(upload.router)
app.include_router(jobs.router)
app.include_router(download.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Forge Audio API", "status": "online"}

@app.get("/debug-cors")
async def debug_cors():
    return {
        "env_var": os.getenv("CORS_ORIGINS"),
        "parsed_origins": origins,
        "allow_all": "*" in origins
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
