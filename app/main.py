import sys
from pathlib import Path
from contextlib import asynccontextmanager

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import TOP_K_RETRIEVAL
from app.retrieval.vector_store import VectorStore
from app.retrieval.reranker import Reranker
from app.generation.responder import LLMResponder


vector_store = None
reranker = None
responder = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global vector_store, reranker, responder
    vector_store = VectorStore()
    reranker = Reranker()
    responder = LLMResponder()
    yield


app = FastAPI(title="FarmaBot API", lifespan=lifespan)

static_dir = Path(__file__).resolve().parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    response: str
    sources: list[str]


class StatsResponse(BaseModel):
    total_chunks: int


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    stats = vector_store.get_collection_stats()
    return StatsResponse(total_chunks=stats.get("total_chunks", 0))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    candidates = vector_store.search(req.query, n_results=TOP_K_RETRIEVAL)

    if not candidates:
        return ChatResponse(
            response="No encontré información relevante en los documentos disponibles para responder tu pregunta.",
            sources=[],
        )

    top_context = reranker.rerank(req.query, candidates)
    respuesta, fuentes = responder.generate(req.query, top_context)
    return ChatResponse(response=respuesta, sources=fuentes)


@app.get("/")
async def index():
    index_file = static_dir / "index.html"
    if not index_file.exists():
        return {"error": "Frontend not found"}
    return FileResponse(str(index_file))
