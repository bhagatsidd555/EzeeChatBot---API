"""
Sentence-aware chunker with sliding window overlap.
Strategy: split on sentence boundaries (not raw characters) to preserve
semantic meaning, then group sentences into chunks of ~CHUNK_SIZE tokens
with CHUNK_OVERLAP token overlap between consecutive chunks.
This avoids cutting mid-sentence and preserves metadata (source, chunk index).
"""

import re
import tiktoken
from app.config import settings

enc = tiktoken.get_encoding("cl100k_base")


def _count_tokens(text: str) -> int:
    return len(enc.encode(text))


def _split_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+|\n{2,}', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text: str, source: str = "text") -> list[dict]:
    """
    Returns list of chunk dicts:
    { "text": str, "source": str, "chunk_index": int, "token_count": int }
    """
    sentences = _split_sentences(text)
    chunks = []
    current_sentences: list[str] = []
    current_tokens = 0
    chunk_index = 0

    for sentence in sentences:
        s_tokens = _count_tokens(sentence)

        if current_tokens + s_tokens > settings.CHUNK_SIZE and current_sentences:
            chunk_text_str = " ".join(current_sentences)
            chunks.append({
                "text": chunk_text_str,
                "source": source,
                "chunk_index": chunk_index,
                "token_count": current_tokens,
            })
            chunk_index += 1

            overlap_sentences: list[str] = []
            overlap_tokens = 0
            for s in reversed(current_sentences):
                t = _count_tokens(s)
                if overlap_tokens + t > settings.CHUNK_OVERLAP:
                    break
                overlap_sentences.insert(0, s)
                overlap_tokens += t

            current_sentences = overlap_sentences
            current_tokens = overlap_tokens

        current_sentences.append(sentence)
        current_tokens += s_tokens

    if current_sentences:
        chunks.append({
            "text": " ".join(current_sentences),
            "source": source,
            "chunk_index": chunk_index,
            "token_count": current_tokens,
        })

    return chunks