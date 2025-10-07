from __future__ import annotations

import os
from typing import List, Sequence

import psycopg
from fastapi import FastAPI, HTTPException, Query
from sentence_transformers import SentenceTransformer


def _require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Expected environment variable {key!r} to be set")
    return value


def _vector_literal(values: Sequence[float]) -> str:
    """Format a list of floats for pgvector (avoids requiring a custom adapter)."""
    return "[" + ",".join(f"{value:.7f}" for value in values) + "]"


DB_URL = _require_env("DATABASE_URL")
MODEL_NAME = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")

app = FastAPI(title="Charity Compass API")
model = SentenceTransformer(MODEL_NAME)


@app.get("/health")
def read_health() -> dict[str, bool]:
    return {"ok": True}


@app.get("/search")
def search(q: str = Query(..., min_length=2), k: int = Query(10, ge=1, le=50)) -> List[dict[str, float | str]]:
    """Hybrid vector + keyword search across ingested document chunks."""
    query_vector = model.encode([q], normalize_embeddings=True)[0].tolist()
    vector_param = _vector_literal(query_vector)

    try:
        with psycopg.connect(DB_URL) as conn, conn.cursor() as cur:
            cur.execute(
                """
                WITH v AS (
                  SELECT id,
                         org_id,
                         title,
                         chunk,
                         1 / (1 + (embedding <-> %s::vector)) AS vscore
                  FROM docs
                  WHERE embedding IS NOT NULL
                  ORDER BY embedding <-> %s::vector
                  LIMIT 30
                ),
                t AS (
                  SELECT id,
                         org_id,
                         title,
                         chunk,
                         ts_rank_cd(to_tsvector('english', chunk), plainto_tsquery('english', %s)) AS tscore
                  FROM docs
                  WHERE to_tsvector('english', chunk) @@ plainto_tsquery('english', %s)
                  ORDER BY tscore DESC
                  LIMIT 30
                )
                SELECT id,
                       org_id,
                       title,
                       chunk,
                       COALESCE(v.vscore * 0.6, 0) + COALESCE(t.tscore * 0.4, 0) AS score
                FROM v
                FULL OUTER JOIN t USING (id, org_id, title, chunk)
                ORDER BY score DESC
                LIMIT %s;
                """,
                (vector_param, vector_param, q, q, k),
            )
            rows = cur.fetchall()
    except psycopg.Error as exc:
        raise HTTPException(status_code=500, detail="Database query failed") from exc

    return [
        {"title": row[2], "chunk": row[3], "score": float(row[4])}
        for row in rows
        if row[2] is not None and row[3] is not None
    ]
