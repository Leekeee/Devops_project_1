-- DATABASE TIER — Initial schema
-- Runs automatically on first container startup (data volume empty).
-- Safe to re-run thanks to IF NOT EXISTS.

CREATE TABLE IF NOT EXISTS todos (
    id        SERIAL      PRIMARY KEY,
    title     TEXT        NOT NULL,
    completed BOOLEAN     NOT NULL DEFAULT FALSE,
    created   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Optional: seed a couple of sample rows on first boot
INSERT INTO todos (title) VALUES
    ('Dockerize the app ✅'),
    ('Add more features')
ON CONFLICT DO NOTHING;
