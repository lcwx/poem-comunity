import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import embed, search
from app.models import PoemResult, SearchRequest, SearchResponse

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 仅本地后端需要预加载模型（避免首次请求阻塞）；
    # api 后端无本地模型，跳过，启动更快、也不依赖 torch。
    if os.getenv("EMBED_BACKEND", "local").lower() != "api":
        embed.get_model()
    yield


app = FastAPI(title="poem-comunity API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/search", response_model=SearchResponse)
def search_poems(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query cannot be empty")
    limit = max(1, min(req.limit, 50))
    results = search.search(req.query, limit, req.dynasties or None)
    return SearchResponse(results=results, query=req.query)


@app.get("/dynasties")
def list_dynasties():
    client = search.get_client()
    seen: set[str] = set()
    offset = None
    while True:
        results, offset = client.scroll(
            search.COLLECTION, limit=500, offset=offset, with_payload=["dynasty"]
        )
        for p in results:
            if p.payload and p.payload.get("dynasty"):
                seen.add(p.payload["dynasty"])
        if offset is None:
            break
    return sorted(seen)


@app.get("/poem/{poem_id}", response_model=PoemResult)
def get_poem(poem_id: str):
    poem = search.get_by_id(poem_id)
    if poem is None:
        raise HTTPException(status_code=404, detail="poem not found")
    return poem


@app.get("/poems/random", response_model=list[PoemResult])
def random_poems(limit: int = 6):
    limit = max(1, min(limit, 20))
    return search.random_poems(limit)


@app.get("/health")
def health():
    return {"status": "ok"}
