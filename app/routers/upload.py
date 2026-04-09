import uuid
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.chunker import chunk_text
from app.services.embedder import embed_texts
from app.services.vector_store import upsert_chunks
from app.config import settings

router = APIRouter()


class UploadRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None


@router.post("/upload")
async def upload(req: UploadRequest):
    if not req.text and not req.url:
        raise HTTPException(status_code=400, detail="Provide either 'text' or 'url'.")

    if req.url:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(str(req.url))
                resp.raise_for_status()
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                raw_text = soup.get_text(separator=" ", strip=True)
                source = str(req.url)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Failed to fetch URL: {e}")
    else:
        raw_text = req.text
        source = "text_upload"

    if not raw_text or len(raw_text.strip()) < 50:
        raise HTTPException(status_code=422, detail="Content is too short to process.")

    chunks = chunk_text(raw_text, source=source)
    if not chunks:
        raise HTTPException(status_code=422, detail="No chunks could be extracted.")

    texts = [c["text"] for c in chunks]
    embeddings, embed_tokens = await embed_texts(texts)

    bot_id = str(uuid.uuid4())
    upsert_chunks(bot_id, chunks, embeddings)

    _init_stats(bot_id, embed_tokens, len(chunks))

    return {
        "bot_id": bot_id,
        "chunks_stored": len(chunks),
        "source": source,
        "embedding_tokens_used": embed_tokens,
    }


import json
import os

STATS_DIR = "./bot_stats"
os.makedirs(STATS_DIR, exist_ok=True)


def _init_stats(bot_id: str, embed_tokens: int, num_chunks: int):
    path = f"{STATS_DIR}/{bot_id}.json"
    embed_cost = (embed_tokens / 1_000_000) * settings.EMBEDDING_COST_PER_1M
    data = {
        "bot_id": bot_id,
        "total_messages": 0,
        "total_latency_ms": 0,
        "unanswered_count": 0,
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "embedding_cost_usd": round(embed_cost, 6),
        "num_chunks": num_chunks,
    }
    with open(path, "w") as f:
        json.dump(data, f)