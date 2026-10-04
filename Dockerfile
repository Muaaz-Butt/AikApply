# One container: Django API + built React app + headless Chromium for auto-apply.
# Built and run by Hugging Face Spaces (Docker SDK), listening on port 7860.

# ── 1. Build the React frontend ──────────────────────────────────────────────
FROM node:20-slim AS frontend
WORKDIR /frontend
COPY fyp-frontend1/package.json fyp-frontend1/package-lock.json ./
RUN npm ci
COPY fyp-frontend1/ ./
# Empty API base = call the same origin that serves the app
ENV VITE_API_URL=""
RUN npm run build

# ── 2. Django + Chromium runtime ─────────────────────────────────────────────
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends chromium chromium-driver fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face runs containers as uid 1000
RUN useradd -m -u 1000 user

ENV PYTHONUNBUFFERED=1 \
    DJANGO_DEBUG=0 \
    AUTOMATION_HEADLESS=1 \
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    FRONTEND_DIST=/app/frontend_dist \
    PORT=7860

WORKDIR /app
COPY backend-fyp/aikapply/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user backend-fyp/aikapply/ /app/
COPY --chown=user --from=frontend /frontend/dist /app/frontend_dist
COPY --chown=user deploy/start.sh /app/start.sh
RUN chmod +x /app/start.sh && mkdir -p /app/media /app/staticfiles && chown -R user:user /app

USER user
EXPOSE 7860
CMD ["/app/start.sh"]
