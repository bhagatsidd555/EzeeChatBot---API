import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Ollama config
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

    # Cost (FREE for Ollama)
    EMBEDDING_COST_PER_1M: float = 0.0
    INPUT_COST_PER_1M: float = 0.0
    OUTPUT_COST_PER_1M: float = 0.0

    # Chunking
    CHUNK_SIZE: int = 400
    CHUNK_OVERLAP: int = 60
    TOP_K_CHUNKS: int = 5

    # Fallback detection
    NO_ANSWER_PHRASES: list = [
        "i don't know", "not mentioned", "cannot find",
        "no information", "not in the document", "i cannot answer"
    ]

settings = Settings()