# Backend build
FROM python:3.11-slim AS backend

WORKDIR /app/backend
COPY ./backend /app/backend

RUN pip install --no-cache-dir -r requirements.txt

# Frontend build
FROM node:18 AS frontend
WORKDIR /app/frontend
COPY ./frontend /app/frontend

RUN npm install && npm run build

# Production image
FROM python:3.11-slim

WORKDIR /app

# Copy backend
COPY --from=backend /app/backend .

# Copy frontend build to backend static folder (or adjust path as needed)
COPY --from=frontend /app/frontend/dist ./static

EXPOSE 5000

CMD ["python", "app.py"]
