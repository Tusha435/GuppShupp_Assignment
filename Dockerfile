# ---------- Backend build (Flask) ----------
FROM python:3.11-slim AS backend

WORKDIR /app/backend

# Copy backend code from app/backend
COPY app/backend/ /app/backend/

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt


# ---------- Frontend build (React) ----------
FROM node:18 AS frontend

WORKDIR /app/frontend

# Copy frontend code from app/frontend
COPY app/frontend/ /app/frontend/

RUN npm install
RUN npm run build  # if your build folder is "build", see note below


# ---------- Final runtime image ----------
FROM python:3.11-slim

WORKDIR /app

# Copy backend app
COPY --from=backend /app/backend/ .

# Copy React build into a folder Flask can serve
# If your React build output is "build" (CRA default), use that:
# COPY --from=frontend /app/frontend/build ./static
COPY --from=frontend /app/frontend/dist ./static

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# If your main file is different, change this
CMD ["python", "app.py"]
