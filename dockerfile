FROM python:3.12-slim

# Install Node + npm for building frontend
RUN apt-get update && \
    apt-get install -y nodejs npm && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app/

# Backend deps
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# Frontend build
RUN cd frontend && npm install && npm run build

# EXAMPLE: start your backend app
WORKDIR /app/backend
CMD ["python", "app.py"]
