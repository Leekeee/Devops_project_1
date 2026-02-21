"""
BACKEND TIER — Python REST API
Supports PostgreSQL (Docker) and SQLite (local dev) via DATABASE_URL env var.

  Docker:    DATABASE_URL=postgresql://user:pass@db:5432/todos  → PostgreSQL
  Local dev: (no env var)                                        → SQLite
"""

import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# ── Database adapter ──────────────────────────────────────────────────────────

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    if DATABASE_URL:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        return conn
    else:
        import sqlite3
        conn = sqlite3.connect("todos.db")
        conn.row_factory = sqlite3.Row
        return conn

def fetchall(conn, sql, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    if DATABASE_URL:
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]
    return [dict(r) for r in rows]

def fetchone(conn, sql, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    row = cur.fetchone()
    if row is None:
        return None
    if DATABASE_URL:
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))
    return dict(row)

def execute(conn, sql, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    return cur

def P():
    """Parameter placeholder: %s for PostgreSQL, ? for SQLite."""
    return "%s" if DATABASE_URL else "?"

def init_db():
    """Create todos table, retrying to handle Docker startup ordering."""
    for attempt in range(10):
        try:
            with get_db() as conn:
                if DATABASE_URL:
                    execute(conn, """
                        CREATE TABLE IF NOT EXISTS todos (
                            id        SERIAL PRIMARY KEY,
                            title     TEXT        NOT NULL,
                            completed BOOLEAN     NOT NULL DEFAULT FALSE,
                            created   TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                    """)
                    conn.commit()
                else:
                    execute(conn, """
                        CREATE TABLE IF NOT EXISTS todos (
                            id        INTEGER PRIMARY KEY AUTOINCREMENT,
                            title     TEXT    NOT NULL,
                            completed INTEGER NOT NULL DEFAULT 0,
                            created   TEXT    NOT NULL DEFAULT (datetime('now'))
                        )
                    """)
                    conn.commit()
            db_label = ("PostgreSQL → " + DATABASE_URL.split("@")[-1]) if DATABASE_URL else "SQLite → todos.db"
            print(f"✅  Database ready  ({db_label})")
            return
        except Exception as e:
            print(f"⏳  Waiting for DB… attempt {attempt + 1}/10  ({e})")
            time.sleep(2)
    raise RuntimeError("Could not connect to database after 10 attempts.")

# ── HTTP handler ───────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):

    def _send(self, code, data):
        body = json.dumps(data, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type",   "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n)) if n else {}

    def log_message(self, fmt, *args):
        print(f"  {self.command:7s}  {self.path}  →  {args[1]}")

    def _parts(self):
        return [p for p in self.path.strip("/").split("/") if p]

    def do_OPTIONS(self):
        self._send(204, {})

    # GET /todos  or  GET /todos/<id>
    def do_GET(self):
        parts = self._parts()
        if not parts or parts[0] != "todos":
            return self._send(404, {"error": "Not found"})
        ph = P()
        with get_db() as conn:
            if len(parts) == 2 and parts[1].isdigit():
                row = fetchone(conn, f"SELECT * FROM todos WHERE id={ph}", (parts[1],))
                return self._send(200, row) if row else self._send(404, {"error": "Todo not found"})
            rows = fetchall(conn, "SELECT * FROM todos ORDER BY created DESC")
            return self._send(200, rows)

    # POST /todos
    def do_POST(self):
        if not self.path.startswith("/todos"):
            return self._send(404, {"error": "Not found"})
        title = (self._body().get("title") or "").strip()
        if not title:
            return self._send(400, {"error": "title is required"})
        ph = P()
        with get_db() as conn:
            if DATABASE_URL:
                cur = execute(conn, f"INSERT INTO todos (title) VALUES ({ph}) RETURNING *", (title,))
                row = dict(zip([d[0] for d in cur.description], cur.fetchone()))
            else:
                cur = execute(conn, f"INSERT INTO todos (title) VALUES ({ph})", (title,))
                row = fetchone(conn, f"SELECT * FROM todos WHERE id={ph}", (cur.lastrowid,))
            conn.commit()
        self._send(201, row)

    # PUT /todos/<id>
    def do_PUT(self):
        parts = self._parts()
        if len(parts) != 2 or not parts[1].isdigit():
            return self._send(400, {"error": "PUT /todos/<id>"})
        ph = P()
        with get_db() as conn:
            row = fetchone(conn, f"SELECT * FROM todos WHERE id={ph}", (parts[1],))
            if not row:
                return self._send(404, {"error": "Todo not found"})
            body      = self._body()
            title     = body.get("title",     row["title"])
            completed = body.get("completed", row["completed"])
            if DATABASE_URL:
                cur = execute(conn,
                    f"UPDATE todos SET title={ph}, completed={ph} WHERE id={ph} RETURNING *",
                    (title, bool(completed), parts[1]))
                updated = dict(zip([d[0] for d in cur.description], cur.fetchone()))
            else:
                execute(conn,
                    f"UPDATE todos SET title={ph}, completed={ph} WHERE id={ph}",
                    (title, int(bool(completed)), parts[1]))
                updated = fetchone(conn, f"SELECT * FROM todos WHERE id={ph}", (parts[1],))
            conn.commit()
        self._send(200, updated)

    # DELETE /todos/<id>
    def do_DELETE(self):
        parts = self._parts()
        if len(parts) != 2 or not parts[1].isdigit():
            return self._send(400, {"error": "DELETE /todos/<id>"})
        ph = P()
        with get_db() as conn:
            cur = execute(conn, f"DELETE FROM todos WHERE id={ph}", (parts[1],))
            conn.commit()
        if cur.rowcount == 0:
            return self._send(404, {"error": "Todo not found"})
        self._send(200, {"deleted": int(parts[1])})


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    server = HTTPServer(("0.0.0.0", 5000), Handler)
    print("🚀  Backend running  →  http://0.0.0.0:5000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋  Server stopped.")
