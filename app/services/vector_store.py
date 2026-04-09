"""
ChromaDB wrapper — each bot_id gets its own isolated collection.
Zero knowledge-base bleed between different bots/clients.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings

_client = chromadb.PersistentClient(
    path=settings.CHROMA_PERSIST_DIR,
    settings=ChromaSettings(anonymized_telemetry=False),
)


def _collection(bot_id: str):
    return _client.get_or_create_collection(
        name=f"bot_{bot_id}",
        metadata={"hnsw:space": "cosine"},
    )


def upsert_chunks(
    bot_id: str,
    chunks: list[dict],
    embeddings: list[list[float]]
) -> None:
    col = _collection(bot_id)
    ids = [f"{bot_id}_{c['chunk_index']}" for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "source": c["source"],
            "chunk_index": c["chunk_index"],
            "token_count": c["token_count"]
        }
        for c in chunks
    ]
    col.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )


def query_chunks(
    bot_id: str,
    query_embedding: list[float],
    top_k: int
) -> list[str]:
    col = _collection(bot_id)
    results = col.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, col.count()),
        include=["documents", "distances"],
    )
    docs = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    # Filter low-relevance chunks
    # cosine distance > 0.7 = poor match
    filtered = [
        doc for doc, dist in zip(docs, distances)
        if dist < 0.7
    ]
    return filtered


def bot_exists(bot_id: str) -> bool:
    try:
        col = _collection(bot_id)
        return col.count() > 0
    except Exception:
        return False