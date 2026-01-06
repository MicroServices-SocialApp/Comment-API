# --- Stage 1: Builder ---
    FROM python:3.13-slim AS builder
    
    WORKDIR /app
    
    # Install build dependencies
    RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        && rm -rf /var/lib/apt/lists/*
    
    # Install requirements to a local directory
    COPY requirements.txt .
    RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
    
    # --- Stage 2: Final ---
    FROM python:3.13-slim
    
    ENV PYTHONDONTWRITEBYTECODE=1
    ENV PYTHONUNBUFFERED=1
    
    WORKDIR /app
    
    # Copy only the installed packages from the builder stage
    COPY --from=builder /install /usr/local
    
    # Copy the rest of the application
    COPY . .
    
    EXPOSE 8000
    
    # Using "exec" form for CMD is generally preferred
    CMD ["sh", "-c", "python db/wait_for_db.py && uvicorn main:app --host 0.0.0.0 --port 8000"]