import json
import os
from fastapi import APIRouter, HTTPException
from app.config import settings

router = APIRouter()

STATS_DIR = "./bot_stats"


@router.get("/stats/{bot_id}")
async def get_stats(bot_id: str):
    path = f"{STATS_DIR}/{bot_id}.json"
    if not os.path.exists(path):
        raise HTTPException(
            status_code=404,
            detail="No stats found for this bot_id."
        )

    with open(path) as f:
        data = json.load(f)

    total_msgs = data["total_messages"]
    avg_latency = (
        round(data["total_latency_ms"] / total_msgs)
        if total_msgs > 0
        else 0
    )

    input_cost = (
        data["total_prompt_tokens"] / 1_000_000
    ) * settings.INPUT_COST_PER_1M

    output_cost = (
        data["total_completion_tokens"] / 1_000_000
    ) * settings.OUTPUT_COST_PER_1M

    total_cost = data["embedding_cost_usd"] + input_cost + output_cost

    return {
        "bot_id": bot_id,
        "total_messages_served": total_msgs,
        "avg_response_latency_ms": avg_latency,
        "estimated_token_cost_usd": round(total_cost, 6),
        "unanswered_questions": data["unanswered_count"],
        "num_chunks_stored": data["num_chunks"],
    }