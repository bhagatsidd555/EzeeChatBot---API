import time
import ollama
from app.config import settings

SYSTEM_TEMPLATE = """You are a helpful assistant. Answer the user's question using ONLY the context provided below.

RULES:
1. If the answer is in the context, answer clearly and concisely.
2. If the answer is NOT in the context, respond with exactly: "I cannot find this information in the uploaded document."
3. Do NOT use any external knowledge. Do NOT guess or infer beyond the context.

CONTEXT:
{context}
"""

FALLBACK_MESSAGE = "I cannot find this information in the uploaded document."


async def stream_chat_response(
    chunks: list[str],
    user_message: str,
    conversation_history: list[dict],
):
    if not chunks:
        yield FALLBACK_MESSAGE, {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "no_answer": True,
            "latency_ms": 0,
        }
        return

    context = "\n\n---\n\n".join(chunks)
    system_prompt = SYSTEM_TEMPLATE.format(context=context)

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history[-6:])
    messages.append({"role": "user", "content": user_message})

    start = time.time()
    full_response = ""

    stream = ollama.chat(
        model=settings.LLM_MODEL,
        messages=messages,
        stream=True,
    )

    for chunk in stream:
        delta = chunk["message"]["content"]
        if delta:
            full_response += delta
            yield delta, None

    latency_ms = int((time.time() - start) * 1000)
    prompt_tokens = len(system_prompt.split())
    completion_tokens = len(full_response.split())

    lower = full_response.lower()
    no_answer = any(phrase in lower for phrase in settings.NO_ANSWER_PHRASES)

    yield "", {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "no_answer": no_answer,
        "latency_ms": latency_ms,
    }