"""
Tiny shared PostgreSQL connection helper for FastAPI routes.

Reads connection settings from env vars (set in .env for local dev,
azd / Container Apps secrets in deployed environments) and returns a
psycopg2 connection with a RealDictCursor so route handlers can return
JSON-friendly dicts directly.
"""
from __future__ import annotations

import os
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor


def _env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name, default)
    return value


def get_connection(**overrides: Any):
    """
    Return a new psycopg2 connection with RealDictCursor and SSL.

    Callers are responsible for closing the connection. Typical usage:

        conn = get_connection()
        try:
            with conn, conn.cursor() as cur:
                cur.execute(...)
        finally:
            conn.close()
    """
    params = {
        "host": _env("POSTGRES_HOST", "ci-ci-dev-pgflex.postgres.database.azure.com"),
        "database": _env("POSTGRES_DATABASE", "cipgraph"),
        "user": _env("POSTGRES_USER", "pgadmin"),
        "password": _env("POSTGRES_ADMIN_PASSWORD"),
        "sslmode": _env("POSTGRES_SSLMODE", "require"),
        "cursor_factory": RealDictCursor,
        "connect_timeout": 30,
    }
    params.update(overrides)
    return psycopg2.connect(**params)
