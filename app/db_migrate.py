"""Tiny migration helper for SQLite.

This project avoids a full migration stack to keep the zip self-contained.
On startup we check for missing columns/tables and add them if needed.

NOTE: For production, prefer Alembic/Flask-Migrate.
"""

from __future__ import annotations

from sqlalchemy import text


def _has_column(conn, table: str, column: str) -> bool:
    rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return any(r[1] == column for r in rows)


def run_sqlite_migrations(db):
    engine = db.engine
    with engine.begin() as conn:
        # reminders table: add columns if this is an older DB
        if conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='reminders'")).fetchone():
            if not _has_column(conn, 'reminders', 'active'):
                conn.execute(text("ALTER TABLE reminders ADD COLUMN active BOOLEAN DEFAULT 1"))
            if not _has_column(conn, 'reminders', 'next_run_at'):
                conn.execute(text("ALTER TABLE reminders ADD COLUMN next_run_at DATETIME"))
            if not _has_column(conn, 'reminders', 'last_sent_at'):
                conn.execute(text("ALTER TABLE reminders ADD COLUMN last_sent_at DATETIME"))

        # push_subscriptions table
        if not conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='push_subscriptions'"))\
            .fetchone():
            conn.execute(
                text(
                    """
                    CREATE TABLE push_subscriptions (
                        id INTEGER PRIMARY KEY,
                        endpoint TEXT NOT NULL UNIQUE,
                        p256dh TEXT NOT NULL,
                        auth TEXT NOT NULL,
                        created_at DATETIME
                    )
                    """
                )
            )
