# ---------- Frontend build (React) ----------
FROM node:18 AS frontend

WORKDIR /app/frontend

# Copy frontend code
COPY frontend/ ./

RUN npm install
RUN npm run build    # assumes build output = ./build


# ---------- Backend + runtime (Flask) ----------
FROM python:3.11-slim

WORKDIR /app

# Copy backend code
COPY backend/ ./ 

# Install Python deps (includes Flask)
RUN pip install --no-cache-dir -r requirements.txt

# Copy built React app into ./static (or wherever you serve from)
COPY --from=frontend /app/frontend/build ./static

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# If your entry file is app_with_auth.py, change app.py below
CMD ["python", "app_with_auth.py"]

