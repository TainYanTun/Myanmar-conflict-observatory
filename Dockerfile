# --- Production Runtime ---
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
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

# Expose FastAPI port
EXPOSE 8000

# Healthcheck to monitor FastAPI status
HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

# Entrypoint for the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
