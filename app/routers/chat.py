import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.embedder import embed_query
from app.services.vector_store import query_chunks, bot_exists
from app.services.llm import stream_chat_response
from app.config import settings

router = APIRouter()

STATS_DIR = "./bot_stats"


class ChatRequest(BaseModel):
    bot_id: str
    user_message: str
    conversation_history: list[dict] = []


@router.post("/chat")
async def chat(req: ChatRequest):
    if not bot_exists(req.bot_id):
        raise HTTPException(
            status_code=404,
            detail="bot_id not found. Upload content first."
        )

    query_emb, query_tokens = await embed_query(req.user_message)

    relevant_chunks = query_chunks(
        req.bot_id,
        query_emb,
        top_k=settings.TOP_K_CHUNKS
    )

    async def event_stream():
        usage = {}
        async for delta, meta in stream_chat_response(
            relevant_chunks,
            req.user_message,
            req.conversation_history
        ):
            if delta:
                yield delta
            if meta:
                usage = meta

        _update_stats(req.bot_id, usage, query_tokens)

    return StreamingResponse(event_stream(), media_type="text/plain")


def _update_stats(bot_id: str, usage: dict, query_tokens: int):
    path = f"{STATS_DIR}/{bot_id}.json"
    try:
        with open(path) as f:
            data = json.load(f)

        data["total_messages"] += 1
        data["total_latency_ms"] += usage.get("latency_ms", 0)
        data["unanswered_count"] += 1 if usage.get("no_answer") else 0
        data["total_prompt_tokens"] += usage.get("prompt_tokens", 0) + query_tokens
        data["total_completion_tokens"] += usage.get("completion_tokens", 0)

        with open(path, "w") as f:
            json.dump(data, f)
    except Exception:
        pass