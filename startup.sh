#!/bin/bash

# Myanmar Conflict Observatory - Production Startup Script

echo "--- INITIALIZING SYSTEM DATA ---"

# Data is loaded from Supabase PostgreSQL at app startup via DB_URL
# or falls back to CSV in data/ directory

echo "--- LAUNCHING DASHBOARD ---"

exec uvicorn server:app --host 0.0.0.0 --port 8000
