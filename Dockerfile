# ---------- Frontend build (React) ----------
FROM node:18 AS frontend

WORKDIR /frontend

# Install deps first for better caching
COPY frontend/package*.json ./
RUN npm install

# Copy rest of frontend and build
COPY frontend/ ./
RUN npm run build    # creates /frontend/build


# ---------- Backend + runtime (Flask) ----------
FROM python:3.11-slim

WORKDIR /app

# Copy backend code
COPY backend/ ./ 

# Install Python deps (must include Flask)
RUN pip install --no-cache-dir -r requirements.txt

# Copy React build into /app/frontend_build
COPY --from=frontend /frontend/build ./frontend_build

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# If your entry file is app_with_auth.py, keep this:
CMD ["python", "app_with_auth.py"]
