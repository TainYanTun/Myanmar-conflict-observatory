#!/bin/bash

# Myanmar Conflict Observatory - Production Startup Script

echo "--- INITIALIZING SYSTEM DATA ---"

# 1. Fetch latest data from ACLED API
echo "Step 1: Synchronizing with ACLED API..."
python update_data.py

# 2. Ingest into PostgreSQL (if DB_URL is present)
if [ -z "$DB_URL" ]; then
    echo "Notice: DB_URL not set. Running in CSV-only mode."
else
    echo "Step 2: Ingesting data into PostgreSQL..."
    python db_manager.py
fi

echo "--- DATA SYNCHRONIZATION COMPLETE ---"

# 3. Start the dashboard
echo "Step 3: Launching Streamlit Dashboard..."
exec streamlit run app.py
