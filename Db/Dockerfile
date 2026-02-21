# ── DATABASE TIER ──────────────────────────────────────────
# PostgreSQL with an automatic schema init script.
# The official image runs any *.sql file placed in
# /docker-entrypoint-initdb.d/ on first startup.
# ───────────────────────────────────────────────────────────

FROM postgres:16-alpine

# Copy the schema — runs once when the data volume is empty
COPY init.sql /docker-entrypoint-initdb.d/01-init.sql

# Postgres listens on 5432 by default
EXPOSE 5432

# Default healthcheck using pg_isready (built into the image)
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s \
  CMD pg_isready -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" || exit 1
