# ── FRONTEND TIER ──────────────────────────────────────────
# Serves the static HTML/CSS/JS via nginx
# ───────────────────────────────────────────────────────────

FROM nginx:alpine

# Copy static frontend files into nginx's web root
COPY index.html /usr/share/nginx/html/index.html

# Copy custom nginx config (handles API proxying + SPA routing)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=3s \
  CMD wget -qO- http://localhost/health || exit 1
