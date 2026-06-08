"""Embedding 后端抽象。

通过环境变量 EMBED_BACKEND 切换：
- "local"（默认）：本地加载 BAAI/bge-m3（FlagEmbedding），用于离线批量建索引。
- "api"：调用 SiliconFlow 等托管的 BGE-M3 接口，用于线上 query 编码，
  无需 torch/FlagEmbedding，镜像更小、启动更快。

两种后端都输出 1024 维、L2 归一化的 dense 向量，与已建好的 Qdrant 索引对齐。
"""
import math
import os
from pathlib import Path

# 本地模型缓存：仅 local 后端会用到（延迟 import，避免 api 镜像依赖 torch）
_model = None

_IGNORE = [
    "flax_model.msgpack", "rust_model.ot", "tf_model.h5",
    "*.DS_Store", ".DS_Store", "imgs/.DS_Store",
]


def _backend() -> str:
    return os.getenv("EMBED_BACKEND", "local").lower()


# ---------------------------------------------------------------------------
# local 后端：FlagEmbedding BGE-M3
# ---------------------------------------------------------------------------

def _resolve_model_path() -> str:
    from huggingface_hub import snapshot_download

    model_name = os.getenv("BGE_MODEL_NAME", "BAAI/bge-m3")
    # 如果已经是本地路径就直接用
    if Path(model_name).exists():
        return model_name
    # HF_HOME 是 HuggingFace 顶层目录，模型缓存在其下的 hub 子目录；
    # snapshot_download 的 cache_dir 需要直接指向 hub 层。
    hf_home = os.getenv("HF_HOME")
    if hf_home:
        cache_dir = str(Path(hf_home) / "hub")
    else:
        cache_dir = str(Path.home() / ".cache" / "huggingface" / "hub")
    return snapshot_download(
        repo_id=model_name,
        cache_dir=cache_dir,
        ignore_patterns=_IGNORE,
    )


def get_model():
    """加载并缓存本地 BGE-M3 模型。仅 local 后端调用。"""
    global _model
    if _model is None:
        from FlagEmbedding import BGEM3FlagModel

        model_path = _resolve_model_path()
        _model = BGEM3FlagModel(model_path, use_fp16=True)
    return _model


def _encode_local(texts: list[str]) -> list[list[float]]:
    model = get_model()
    output = model.encode(
        texts,
        batch_size=32,
        max_length=512,
        return_dense=True,
        return_sparse=False,
        return_colbert_vecs=False,
    )
    # FlagEmbedding 的 dense_vecs 已 L2 归一化
    return output["dense_vecs"].tolist()


# ---------------------------------------------------------------------------
# api 后端：SiliconFlow（兼容 OpenAI embeddings 协议）
# ---------------------------------------------------------------------------

def _l2_normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0:
        return vec
    return [x / norm for x in vec]


def _encode_api(texts: list[str]) -> list[list[float]]:
    import httpx

    base = os.getenv("EMBED_API_BASE", "https://api.siliconflow.cn/v1")
    model = os.getenv("EMBED_API_MODEL", "BAAI/bge-m3")
    api_key = os.getenv("EMBED_API_KEY")
    if not api_key:
        raise RuntimeError("EMBED_BACKEND=api 但未设置 EMBED_API_KEY")

    # SiliconFlow 单次请求的 input 数量有限，分批发送
    batch_size = int(os.getenv("EMBED_API_BATCH", "32"))
    headers = {"Authorization": f"Bearer {api_key}"}
    out: list[list[float]] = []

    with httpx.Client(timeout=60) as client:
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            resp = client.post(
                f"{base}/embeddings",
                headers=headers,
                json={"model": model, "input": batch, "encoding_format": "float"},
            )
            resp.raise_for_status()
            data = resp.json()["data"]
            # 按 index 排序，确保与输入顺序一致
            data.sort(key=lambda d: d["index"])
            # 显式归一化，保证与本地 BGE-M3 输出在同一空间（防托管端未归一化）
            out.extend(_l2_normalize(d["embedding"]) for d in data)
    return out


# ---------------------------------------------------------------------------
# 统一入口
# ---------------------------------------------------------------------------

def encode(texts: list[str]) -> list[list[float]]:
    if _backend() == "api":
        return _encode_api(texts)
    return _encode_local(texts)
