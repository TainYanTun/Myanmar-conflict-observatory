# --- Stage 1: Build & Runtime ---
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Install system dependencies for GeoPandas and PostGIS/PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application and set ownership to the non-root user
COPY --chown=appuser:appgroup . .

# Switch to the non-root user
USER appuser

# Expose Streamlit port
EXPOSE 8501

# Healthcheck to monitor Streamlit status
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Entrypoint for the application
CMD ["streamlit", "run", "app.py"]
