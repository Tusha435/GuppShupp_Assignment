# --- Build stage ---
FROM python:3.11-slim AS build

WORKDIR /app

# Install Node + npm for frontend build
RUN apt-get update && apt-get install -y nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app/

# Install backend dependencies
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# Build frontend
RUN cd frontend && npm install && npm run build

# --- Runtime stage ---
FROM python:3.11-slim

WORKDIR /app

# Copy backend + built frontend from build stage
COPY --from=build /app/backend /app/backend
COPY --from=build /app/frontend /app/frontend

ENV PORT=8000

# Start your backend app (change if needed)
CMD ["python", "backend/main.py"]
