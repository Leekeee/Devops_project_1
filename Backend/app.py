"""
BACKEND TIER — Flask REST API
Database: SQLite (via Python's built-in sqlite3)
Run: python app.py
API runs on http://localhost:5000
"""

import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer

DB_PATH = "todos.db"


# ──────────────────────────────────────────
# DATABASE TIER — SQLite helpers
# ──────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                title     TEXT    NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                created   TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
    print(f"✅  Database ready  →  {os.path.abspath(DB_PATH)}")


# ──────────────────────────────────────────
# BACKEND TIER — HTTP request handler
# ──────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):

    # ── CORS + JSON headers ──────────────
    def _send(self, code, data):
        body = json.dumps(data, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def log_message(self, fmt, *args):
        print(f"  {self.command:6s}  {self.path}  →  {args[1]}")

    # ── Preflight ────────────────────────
    def do_OPTIONS(self):
        self._send(204, {})

    # ── GET /todos  or  GET /todos/<id> ──
    def do_GET(self):
        parts = self.path.strip("/").split("/")  # ['todos'] or ['todos','3']
        if parts[0] != "todos":
            return self._send(404, {"error": "Not found"})

        with get_db() as conn:
            if len(parts) == 2 and parts[1].isdigit():
                row = conn.execute("SELECT * FROM todos WHERE id=?", (parts[1],)).fetchone()
                if not row:
                    return self._send(404, {"error": "Todo not found"})
                return self._send(200, dict(row))
            rows = conn.execute("SELECT * FROM todos ORDER BY created DESC").fetchall()
            return self._send(200, [dict(r) for r in rows])

    # ── POST /todos ──────────────────────
    def do_POST(self):
        if not self.path.startswith("/todos"):
            return self._send(404, {"error": "Not found"})
        body = self._read_body()
        title = (body.get("title") or "").strip()
        if not title:
            return self._send(400, {"error": "title is required"})
        with get_db() as conn:
            cur = conn.execute("INSERT INTO todos (title) VALUES (?)", (title,))
            conn.commit()
            row = conn.execute("SELECT * FROM todos WHERE id=?", (cur.lastrowid,)).fetchone()
        self._send(201, dict(row))

    # ── PUT /todos/<id> ──────────────────
    def do_PUT(self):
        parts = self.path.strip("/").split("/")
        if len(parts) != 2 or not parts[1].isdigit():
            return self._send(400, {"error": "PUT /todos/<id>"})
        todo_id = parts[1]
        body = self._read_body()
        with get_db() as conn:
            row = conn.execute("SELECT * FROM todos WHERE id=?", (todo_id,)).fetchone()
            if not row:
                return self._send(404, {"error": "Todo not found"})
            title = body.get("title", row["title"])
            completed = body.get("completed", row["completed"])
            conn.execute(
                "UPDATE todos SET title=?, completed=? WHERE id=?",
                (title, int(bool(completed)), todo_id)
            )
            conn.commit()
            updated = conn.execute("SELECT * FROM todos WHERE id=?", (todo_id,)).fetchone()
        self._send(200, dict(updated))

    # ── DELETE /todos/<id> ───────────────
    def do_DELETE(self):
        parts = self.path.strip("/").split("/")
        if len(parts) != 2 or not parts[1].isdigit():
            return self._send(400, {"error": "DELETE /todos/<id>"})
        with get_db() as conn:
            result = conn.execute("DELETE FROM todos WHERE id=?", (parts[1],))
            conn.commit()
        if result.rowcount == 0:
            return self._send(404, {"error": "Todo not found"})
        self._send(200, {"deleted": int(parts[1])})


# ──────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    server = HTTPServer(("localhost", 5000), Handler)
    print("🚀  Backend running  →  http://localhost:5000")
    print("    Endpoints:")
    print("      GET    /todos")
    print("      POST   /todos        body: {title}")
    print("      PUT    /todos/<id>   body: {title?, completed?}")
    print("      DELETE /todos/<id>")
    print("\nPress Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋  Server stopped.")
