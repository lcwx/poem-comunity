"""
一次性构建向量索引。将 data/ 目录下的语料 JSON embed 后 upsert 到 Qdrant。

用法：
    cd backend
    python scripts/build_index.py

环境变量（可写入 .env）：
    QDRANT_URL      默认 http://localhost:6333
    QDRANT_API_KEY  云服务时填写
    HF_ENDPOINT     HuggingFace 镜像，如 https://hf-mirror.com
"""

import json
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

load_dotenv()

# 将 scripts/ 父目录加入 path，使 app 包可以 import
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.embed import encode

DATA_DIR = Path(__file__).parent.parent / "data"
COLLECTION = "poems"
VECTOR_DIM = 1024   # BGE-M3 dense 维度
BATCH_SIZE = 32


def load_corpus() -> list[dict]:
    poems = []
    for json_file in sorted(DATA_DIR.glob("*.json")):
        raw = json.loads(json_file.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            continue
        if "tang" in json_file.name:
            default_dynasty = "唐"
        elif "songci" in json_file.name:
            default_dynasty = "宋词"
        elif "song" in json_file.name:
            default_dynasty = "宋"
        elif "shijing" in json_file.name:
            default_dynasty = "诗经"
        elif "chuci" in json_file.name:
            default_dynasty = "楚辞"
        elif "modern" in json_file.name:
            default_dynasty = "现代"
        else:
            default_dynasty = "古"
        for idx, item in enumerate(raw):
            raw_content = item.get("paragraphs") or item.get("content") or []
            # modern-poetry 的 paragraphs 是字符串，按句号/换行切分
            if isinstance(raw_content, str):
                content = [s.strip() for s in raw_content.replace("。", "。\n").split("\n") if s.strip()]
            else:
                content = raw_content
            if not content:
                continue
            # 宋词用 rhythmic（词牌名）作为标题
            title = item.get("title") or item.get("rhythmic") or "无题"
            author = item.get("author", "佚名")
            # 用文件名+标题+作者组合保证 id 唯一
            uid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{json_file.name}:{idx}:{title}:{author}"))
            poems.append({
                "id": uid,
                "title": title,
                "author": author,
                "dynasty": item.get("dynasty", default_dynasty),
                "content": content,
            })
    return poems


def ensure_collection(client: QdrantClient):
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
        )
        print(f"Collection '{COLLECTION}' 已创建（维度 {VECTOR_DIM}）")
    else:
        print(f"Collection '{COLLECTION}' 已存在，追加模式")


def build_text(poem: dict) -> str:
    """把一首诗合并成单个字符串用于 embedding"""
    return f"{poem['title']} {poem['author']} {''.join(poem['content'])}"


def main():
    poems = load_corpus()
    if not poems:
        print("未找到语料，请先运行 download_corpus.py")
        return

    print(f"共 {len(poems)} 首，开始构建索引...")

    client = QdrantClient(
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )
    ensure_collection(client)

    total = 0
    for i in range(0, len(poems), BATCH_SIZE):
        batch = poems[i : i + BATCH_SIZE]
        texts = [build_text(p) for p in batch]
        vectors = encode(texts)
        points = [
            PointStruct(
                id=p["id"],
                vector=vec,
                payload=p,
            )
            for p, vec in zip(batch, vectors)
        ]
        client.upsert(collection_name=COLLECTION, points=points)
        total += len(batch)
        print(f"  进度 {total}/{len(poems)}")

    print(f"\n索引构建完成！共 {total} 首诗已入库。")
    print("验证: curl http://localhost:6333/collections/poems")


if __name__ == "__main__":
    main()
