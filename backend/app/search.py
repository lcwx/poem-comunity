import os
import random
from functools import lru_cache
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny, ScoredPoint

from app.embed import encode
from app.models import PoemResult

COLLECTION = "poems"
# 一次拿够前端分页需要的最大量
_PAGE_SIZE = 10
_MAX_RESULTS = 50


def get_client() -> QdrantClient:
    url = os.getenv("QDRANT_URL", "http://localhost:6333")
    api_key = os.getenv("QDRANT_API_KEY")
    return QdrantClient(url=url, api_key=api_key)


def _point_to_result(point: ScoredPoint) -> PoemResult:
    p = point.payload
    return PoemResult(
        id=p["id"],
        title=p["title"],
        author=p["author"],
        dynasty=p["dynasty"],
        content=p["content"],
        score=round(point.score, 4),
    )


@lru_cache(maxsize=512)
def _search_cached(query: str, limit: int, dynasties_key: tuple[str, ...] | None) -> list[PoemResult]:
    """缓存 key = (query, limit, dynasties_tuple)，相同搜索直接返回缓存结果。"""
    client = get_client()
    query_vec = encode([query])[0]

    search_filter = None
    if dynasties_key:
        search_filter = Filter(
            must=[FieldCondition(key="dynasty", match=MatchAny(any=list(dynasties_key)))]
        )

    hits = client.search(
        collection_name=COLLECTION,
        query_vector=query_vec,
        query_filter=search_filter,
        limit=limit,
        with_payload=True,
    )
    return [_point_to_result(h) for h in hits]


def search(query: str, limit: int = 10, dynasties: list[str] | None = None) -> list[PoemResult]:
    dynasties_key = tuple(sorted(dynasties)) if dynasties else None
    return _search_cached(query, limit, dynasties_key)


def get_by_id(poem_id: str) -> PoemResult | None:
    client = get_client()
    results = client.scroll(
        collection_name=COLLECTION,
        scroll_filter={"must": [{"key": "id", "match": {"value": poem_id}}]},
        limit=1,
        with_payload=True,
    )
    points, _ = results
    if not points:
        return None
    p = points[0].payload
    return PoemResult(
        id=p["id"],
        title=p["title"],
        author=p["author"],
        dynasty=p["dynasty"],
        content=p["content"],
        score=1.0,
    )


def random_poems(limit: int = 6) -> list[PoemResult]:
    client = get_client()
    # Qdrant scroll with random offset for variety
    total = client.count(collection_name=COLLECTION).count
    offset = random.randint(0, max(0, total - limit))
    results, _ = client.scroll(
        collection_name=COLLECTION,
        limit=limit,
        offset=offset,
        with_payload=True,
    )
    return [
        PoemResult(
            id=p.payload["id"],
            title=p.payload["title"],
            author=p.payload["author"],
            dynasty=p.payload["dynasty"],
            content=p.payload["content"],
            score=1.0,
        )
        for p in results
    ]
