#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
PostgreSQL pgvector VectorStore for GraphRAG v3

Custom VectorStore implementation that uses PostgreSQL + pgvector extension,
allowing GraphRAG and the Contract Intelligence agent to share a single
PostgreSQL Flexible Server instance.

Implements the graphrag_vectors.VectorStore v3 interface (simplified):
  - connect(), create_index(), load_documents(), search_by_id(),
    similarity_search_by_vector()

Usage:
    from graphrag_vectors import register_vector_store
    from backend.vector_stores.pgvector_store import PgVectorStore

    register_vector_store("pgvector", PgVectorStore)
"""

import logging
import os
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values

from graphrag_vectors import (
    VectorStore,
    VectorStoreDocument,
    VectorStoreSearchResult,
)

logger = logging.getLogger(__name__)


class PgVectorStore(VectorStore):
    """PostgreSQL + pgvector vector store for GraphRAG v3.

    Tables created: graphrag_vectors_{index_name}
    Columns: id TEXT PK, vector vector({dim})
    """

    def __init__(
        self,
        # Connection params (from settings.yaml or env vars)
        host: str | None = None,
        database: str | None = None,
        user: str | None = None,
        password: str | None = None,
        port: int = 5432,
        sslmode: str = "require",
        # VectorStore params
        index_name: str = "vector_index",
        vector_size: int = 1536,
        **kwargs: Any,
    ):
        # Resolve connection params from kwargs or environment
        self.host = host or os.environ.get("POSTGRES_HOST", "localhost")
        self.database = database or os.environ.get("POSTGRES_DATABASE", "cipgraph")
        self.user = user or os.environ.get("POSTGRES_USER", "pgadmin")
        self.password = password or os.environ.get("POSTGRES_ADMIN_PASSWORD", "")
        self.port = port
        self.sslmode = sslmode
        self.vector_size = vector_size
        self.index_name = index_name

        # Sanitized table name
        safe_name = index_name.replace("-", "_").replace(" ", "_").lower()
        self.table_name = f"graphrag_vectors_{safe_name}"

        self._conn = None

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """Connect to PostgreSQL and ensure pgvector extension exists."""
        try:
            self._conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                sslmode=self.sslmode,
                cursor_factory=RealDictCursor,
                connect_timeout=30,
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5,
            )
            self._conn.autocommit = False

            with self._conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                self._conn.commit()

            logger.info("PgVectorStore connected to %s/%s", self.host, self.database)
        except psycopg2.Error as e:
            logger.error("PgVectorStore connection failed: %s", e)
            raise

    def _get_conn(self):
        """Get a live connection, reconnecting if needed."""
        if self._conn is None or self._conn.closed:
            self.connect()
        return self._conn

    # ------------------------------------------------------------------
    # Index (table) management
    # ------------------------------------------------------------------

    def create_index(self) -> None:
        """Create the pgvector table and HNSW index if they don't exist."""
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id TEXT PRIMARY KEY,
                    vector vector({self.vector_size})
                );
            """)
            # HNSW index for fast cosine ANN search
            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{self.table_name}_hnsw
                ON {self.table_name}
                USING hnsw (vector vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """)
            conn.commit()
        logger.info("PgVectorStore index created: %s", self.table_name)

    # ------------------------------------------------------------------
    # Document operations
    # ------------------------------------------------------------------

    def load_documents(self, documents: list[VectorStoreDocument]) -> None:
        """Batch load documents with efficient execute_values."""
        if not documents:
            return

        conn = self._get_conn()
        rows = []
        for doc in documents:
            vector_str = self._vector_to_str(doc.vector)
            rows.append((str(doc.id), vector_str))

        with conn.cursor() as cur:
            execute_values(
                cur,
                f"""
                INSERT INTO {self.table_name} (id, vector)
                VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                    vector = EXCLUDED.vector;
                """,
                rows,
                template="(%s, %s::vector)",
                page_size=500,
            )
            conn.commit()

        logger.info(
            "PgVectorStore loaded %d documents into %s",
            len(documents),
            self.table_name,
        )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def similarity_search_by_vector(
        self,
        query_embedding: list[float],
        k: int = 10,
    ) -> list[VectorStoreSearchResult]:
        """ANN search using pgvector cosine distance (<=>)."""
        conn = self._get_conn()
        query_str = self._vector_to_str(query_embedding)

        sql = f"""
            SELECT id, vector::text,
                   1 - (vector <=> %s::vector) AS score
            FROM {self.table_name}
            ORDER BY vector <=> %s::vector
            LIMIT %s;
        """

        with conn.cursor() as cur:
            cur.execute(sql, (query_str, query_str, k))
            rows = cur.fetchall()

        results = []
        for row in rows:
            vector = self._parse_pg_vector(row.get("vector"))
            doc = VectorStoreDocument(id=row["id"], vector=vector)
            results.append(VectorStoreSearchResult(document=doc, score=row["score"]))

        return results

    def search_by_id(self, id: str) -> VectorStoreDocument:
        """Retrieve a document by its ID."""
        conn = self._get_conn()

        with conn.cursor() as cur:
            cur.execute(
                f"SELECT id, vector::text FROM {self.table_name} WHERE id = %s;",
                (str(id),),
            )
            row = cur.fetchone()

        if row is None:
            return VectorStoreDocument(id=id, vector=None)

        vector = self._parse_pg_vector(row.get("vector"))
        return VectorStoreDocument(id=id, vector=vector)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _vector_to_str(vector: list[float] | None) -> str | None:
        """Convert vector list to pgvector string format '[x,y,z,...]'."""
        if vector is None:
            return None
        return "[" + ",".join(str(float(v)) for v in vector) + "]"

    @staticmethod
    def _parse_pg_vector(pg_str: str | None) -> list[float] | None:
        """Parse pgvector text output '[x,y,z,...]' to list[float]."""
        if not pg_str:
            return None
        clean = pg_str.strip("[]")
        return [float(x) for x in clean.split(",")]

    def __del__(self):
        """Close connection on garbage collection."""
        if self._conn and not self._conn.closed:
            try:
                self._conn.close()
            except Exception:
                pass
