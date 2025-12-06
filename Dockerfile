# ---------- Backend build (Flask) ----------
FROM python:3.11-slim AS backend

WORKDIR /app/backend

# Copy backend code from ./backend
COPY backend/ /app/backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# ---------- Frontend build (React) ----------
FROM node:18 AS frontend

WORKDIR /app/frontend

# Copy frontend code from ./frontend
COPY frontend/ /app/frontend/

RUN npm install
RUN npm run build   # if your build output is 'build', we handle that below


# ---------- Final runtime image ----------
FROM python:3.11-slim

WORKDIR /app

# Copy backend app
COPY --from=backend /app/backend/ .

# Copy React build into a folder Flask can serve.
# If your React build output folder is 'build' (Create React App default),
# this is correct:
COPY --from=frontend /app/frontend/build ./static

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Change this if your main file is named differently
CMD ["python", "app.py"]
