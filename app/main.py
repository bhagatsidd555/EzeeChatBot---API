from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import upload, chat, stats

app = FastAPI(
    title="EzeeChatBot API",
    description="RAG-powered chatbot backend — upload any content, chat with it.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(stats.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


print("hello")