# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目简介

poem-comunity 是一个基于语义检索的诗词阅读社区。用户用自然语言描述（"写离别的诗"、"思乡之情"）检索古典诗词，后续扩展为 UGC 诗社社区。

**技术栈：**
- 后端：Python FastAPI + BGE-M3 embedding + Qdrant 向量数据库
- Web：Next.js 14 App Router + TypeScript + Tailwind CSS
- Android：Kotlin + Jetpack Compose（规划中）

## 目录结构

```
backend/
  app/          FastAPI 应用（main.py、embed.py、search.py、models.py）
  scripts/      一次性脚本（download_corpus.py、build_index.py）
  data/         语料 JSON（不提交 git）
web/            Next.js 前端
android/        Kotlin/Compose（待填充）
docker-compose.yml  本地 Qdrant
```

## 常用命令

### 后端

```powershell
# 启动本地 Qdrant（需先拉取镜像，建议配置代理）
cd C:\dev\repo\poem-comunity && docker compose up -d

# 安装依赖（建议 venv）
cd backend && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 下载语料（使用 jsdelivr CDN，无需代理）
cd backend && python scripts/download_corpus.py

# 一次性构建向量索引（首次约 10-30 分钟，取决于 CPU）
cd backend && python scripts/build_index.py

# 启动 API 服务
cd backend && uvicorn app.main:app --reload --port 8000
```

BGE-M3 模型权重约 2.3GB，首次运行自动从 HuggingFace 下载。配置镜像：
```powershell
$env:HF_ENDPOINT="https://hf-mirror.com"
```

### Web 前端

```powershell
cd web && npm install && npm run dev     # 开发服务器 :3000
cd web && npm run build && npm start     # 生产构建
```

### 测试 API

```powershell
# 健康检查
curl http://localhost:8000/health

# 语义搜索
curl -X POST http://localhost:8000/search -H "Content-Type: application/json" -d "{\"query\":\"思念家乡\",\"limit\":5}"

# 随机推荐
curl http://localhost:8000/poems/random
```

## 架构关键点

### Embedding 流程

- 语料是固定的，`build_index.py` 一次性把所有诗 embed 后存入 Qdrant（payload 含完整诗词数据）
- 运行时只需对用户查询字符串做一次 `encode()` → Qdrant cosine 检索，不查其他 DB
- `embed.py` 中的模型是单例（`_model`），FastAPI lifespan 预热，避免首次请求延迟

### 诗词文本格式

`build_index.py` 中 `build_text()` 将 `{title} {author} {content joined}` 拼成一个字符串做 embedding。这比只 embed 标题检索效果好得多（古诗标题往往不反映语义）。

### Qdrant Payload

每个 point 的 payload 存完整字段（id、title、author、dynasty、content），搜索结果直接返回，无需二次查库。

### 环境变量

后端从 `backend/.env` 读取（参考 `.env.example`）：
- `QDRANT_URL` — 本地用 `http://localhost:6333`，云服务替换此值
- `QDRANT_API_KEY` — 云服务鉴权
- `HF_ENDPOINT` — HuggingFace 镜像（国内必填）

### Web → 后端代理

开发环境：`next.config.mjs` 将 `/api/*` rewrite 到 `http://localhost:8000/*`，前端统一用 `/api/search`、`/api/poem/:id` 等路径。生产环境设 `BACKEND_URL` 环境变量指向真实后端。

## 代理配置（国内环境）

```powershell
# Docker 拉取镜像
$env:HTTP_PROXY="http://127.0.0.1:7890"; $env:HTTPS_PROXY="http://127.0.0.1:7890"

# pip 用清华镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# npm 用淘宝镜像
npm config set registry https://registry.npmmirror.com
```
