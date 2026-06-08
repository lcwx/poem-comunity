import os
import random
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny, ScoredPoint

from app.embed import encode
from app.models import PoemResult

COLLECTION = "poems"


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


def search(query: str, limit: int = 10, dynasties: list[str] | None = None) -> list[PoemResult]:
    client = get_client()
    query_vec = encode([query])[0]

    search_filter = None
    if dynasties:
        search_filter = Filter(
            must=[FieldCondition(key="dynasty", match=MatchAny(any=dynasties))]
        )

    hits = client.search(
        collection_name=COLLECTION,
        query_vector=query_vec,
        query_filter=search_filter,
        limit=limit,
        with_payload=True,
    )
    return [_point_to_result(h) for h in hits]


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
