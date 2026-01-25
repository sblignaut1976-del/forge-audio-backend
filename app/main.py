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
origins = [
    origin.strip() 
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") 
    if origin.strip()
]

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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
