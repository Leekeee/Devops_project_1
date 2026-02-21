# ── BACKEND TIER ──────────────────────────────────────────
# Python REST API — connects to PostgreSQL in Docker,
# or falls back to SQLite for local development.
# ───────────────────────────────────────────────────────────

FROM python:3.12-slim

WORKDIR /app

# Install psycopg2 for PostgreSQL support
# (binary build avoids needing libpq-dev / gcc)
RUN pip install --no-cache-dir psycopg2-binary==2.9.9

# Copy application source
COPY app.py .

EXPOSE 5000

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/todos')" \
  || exit 1

CMD ["python", "app.py"]
