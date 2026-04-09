import ollama
from app.config import settings


async def embed_texts(texts: list[str]) -> tuple[list[list[float]], int]:
    all_embeddings = []

    for text in texts:
        response = ollama.embeddings(
            model=settings.EMBEDDING_MODEL,
            prompt=text,
        )
        all_embeddings.append(response["embedding"])

    total_tokens = sum(len(t.split()) for t in texts)
    return all_embeddings, total_tokens


async def embed_query(query: str) -> tuple[list[float], int]:
    response = ollama.embeddings(
        model=settings.EMBEDDING_MODEL,
        prompt=query,
    )
    return response["embedding"], len(query.split())