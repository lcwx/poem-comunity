# 线上后端镜像：EMBED_BACKEND=api，不含 torch/FlagEmbedding。
FROM python:3.11-slim

WORKDIR /app

# 仅装 API 后端依赖
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# 应用代码 + 建索引脚本与语料（线上若需重建索引时用）
COPY app ./app
COPY scripts ./scripts
COPY data ./data

EXPOSE 8000

# 几百人并发：多 worker。embedding 走外部 API，worker 本身很轻。
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
