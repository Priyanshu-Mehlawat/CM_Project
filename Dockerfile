FROM node:22-bookworm-slim AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.14-slim-bookworm
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 RENAL_GUARD_PUBLIC_DEMO=1
COPY requirements-dev.lock ./
RUN pip install --no-cache-dir -r requirements-dev.lock
COPY backend/ ./backend/
COPY ml/ ./ml/
COPY --from=frontend /build/dist ./frontend/dist/
RUN useradd --uid 10001 --create-home app
USER app
EXPOSE 10000
CMD ["sh", "-c", "exec python -m uvicorn backend.app.hosted:app --host 0.0.0.0 --port ${PORT:-10000} --no-access-log --no-proxy-headers"]
