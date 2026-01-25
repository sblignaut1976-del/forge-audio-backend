-- Create jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
    progress FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    stems JSONB, -- Store paths: {"vocals": "...", "drums": "...", ...}
    error_message TEXT
);

-- Create users table (future proofing)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    hashed_password TEXT
);

-- Indexing for performance
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
