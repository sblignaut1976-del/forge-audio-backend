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
os.makedirs("uploads", exist_ok=True)
os.makedirs("stems", exist_ok=True)

# Serve static files for audio stems
app.mount("/stems", StaticFiles(directory="stems"), name="stems")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

from .routes import upload, jobs

# Configure CORS
# Fallback to allowing all if configuration is tricky/ambiguous
raw_origins = os.getenv("CORS_ORIGINS", "*")
if "•" in raw_origins or not raw_origins.strip():
    origins = ["*"]
else:
    origins = [
        origin.strip() 
        for origin in raw_origins.split(",") 
        if origin.strip()
    ]
    # Safety: always Allow all for this debugging phase if * is present anywhere
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
