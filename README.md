# Three-Tier Todo App

A minimal but complete three-tier web application.

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND TIER                      │
│              frontend/index.html                        │
│         HTML · CSS · Vanilla JavaScript                 │
│   • Renders the UI                                      │
│   • Talks to Backend via REST (fetch API)               │
└──────────────────────┬──────────────────────────────────┘
                       │  HTTP  (JSON REST API)
                       │  GET / POST / PUT / DELETE /todos
┌──────────────────────▼──────────────────────────────────┐
│                      BACKEND TIER                       │
│              backend/app.py                             │
│         Python · stdlib HTTPServer (no deps)            │
│   • Exposes REST endpoints                              │
│   • Validates input, handles errors                     │
│   • Talks to Database via SQL                           │
└──────────────────────┬──────────────────────────────────┘
                       │  SQL  (sqlite3)
┌──────────────────────▼──────────────────────────────────┐
│                     DATABASE TIER                       │
│              backend/todos.db  (auto-created)           │
│         SQLite                                          │
│   • Persists todos across restarts                      │
│   • Single table: id, title, completed, created         │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### 1 — Start the backend
```bash
cd backend
python app.py
# ✅  Database ready  →  /path/to/todos.db
# 🚀  Backend running  →  http://localhost:5000
```

### 2 — Open the frontend
Open `frontend/index.html` directly in your browser (double-click it).

That's it — no build step, no npm, no virtual environments.

---

## REST API Reference

| Method | Endpoint      | Body                        | Description           |
|--------|---------------|-----------------------------|-----------------------|
| GET    | /todos        | —                           | List all todos        |
| GET    | /todos/{id}   | —                           | Get a single todo     |
| POST   | /todos        | `{"title": "..."}` | Create a todo         |
| PUT    | /todos/{id}   | `{"title"?, "completed"?}`  | Update a todo         |
| DELETE | /todos/{id}   | —                           | Delete a todo         |

### Example curl commands
```bash
# Create
curl -X POST http://localhost:5000/todos \
     -H "Content-Type: application/json" \
     -d '{"title": "Buy groceries"}'

# List all
curl http://localhost:5000/todos

# Mark done
curl -X PUT http://localhost:5000/todos/1 \
     -H "Content-Type: application/json" \
     -d '{"completed": true}'

# Delete
curl -X DELETE http://localhost:5000/todos/1
```

---

## Database Schema

```sql
CREATE TABLE todos (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    title     TEXT    NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0,   -- 0 = false, 1 = true
    created   TEXT    NOT NULL DEFAULT (datetime('now'))
);
```

---

## File Structure

```
├── backend/
│   └── app.py          ← Python backend (stdlib only, no pip needed)
│   └── todos.db        ← SQLite DB (auto-created on first run)
└── frontend/
│   └── index.html      ← Entire frontend in one file
└── README.md
```

## Extending This App

| Layer    | Swap with              |
|----------|------------------------|
| Frontend | React, Vue, Svelte     |
| Backend  | Flask, FastAPI, Django |
| Database | PostgreSQL, MySQL      |
