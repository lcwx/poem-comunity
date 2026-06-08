# 部署 poem-comunity 到阿里云 ECS

单台 ECS + Docker Compose 部署：Qdrant + 后端(FastAPI) + 前端(Next.js) + Caddy(自动 HTTPS)。
embedding 走 SiliconFlow 托管的 BGE-M3 API（1024 维，与本地索引对齐），所以 CPU 服务器即可，无需 GPU。

```
                浏览器
                  │ HTTP/HTTPS
            ┌─────▼─────┐
            │   Caddy   │  80/443，自动证书
            └─────┬─────┘
            ┌─────▼─────────┐
            │ Next.js :3000 │  /api/* 反代到后端
            └─────┬─────────┘
            ┌─────▼─────────┐    query 编码
            │ FastAPI :8000 ├────────────► SiliconFlow BGE-M3 API
            └─────┬─────────┘
            ┌─────▼─────────┐
            │ Qdrant :6333  │  向量库（内部，不对外）
            └───────────────┘
```

## 一、前置准备

1. 本机安装 [Terraform](https://developer.hashicorp.com/terraform/downloads) ≥ 1.3
2. **阿里云 AccessKey**：控制台 → RAM 访问控制 → 创建用户，授予 ECS / VPC 权限，拿到 AccessKey ID/Secret
3. **SiliconFlow API key**：注册 [siliconflow.cn](https://siliconflow.cn) → 控制台 → API 密钥（用 BGE-M3，1024 维）
4. 代码已推到一个 **git 仓库**（cloud-init 会 clone；私有仓库需在 repo_url 带 token 或换公钥方式）
5. （可选）一个**域名**，想要 HTTPS 就把它解析到 ECS 公网 IP

## 二、用 Terraform 起服务器（推荐）

```bash
cd deploy/terraform
cp terraform.tfvars.example terraform.tfvars
# 编辑 terraform.tfvars，填 access_key/secret_key/instance_password/repo_url/embed_api_key 等
terraform init
terraform plan
terraform apply
```

apply 完成会输出 `public_ip`、`ssh_command`、`site_url`。
ECS 首次开机会自动执行 cloud-init：装 Docker → clone 代码 → 写 `.env` → `docker compose up --build` → 自动建索引。

部署日志在服务器上：

```bash
ssh root@<public_ip>
tail -f /var/log/poem-deploy.log
```

香港地域**免备案**，apply 后几分钟（含建索引）即可用 `site_url` 访问。

### 关于域名 / HTTPS

- 无域名：`site_address = ":80"`，用 `http://<public_ip>` 访问。
- 有域名：先把域名 A 记录解析到 ECS 公网 IP，再设 `site_address = "poems.example.com"`，Caddy 自动签发 Let's Encrypt 证书。
- 大陆地域（非香港）域名解析到服务器**必须先 ICP 备案**（1–3 周）；香港无此限制。

## 三、索引数据：两种方式

cloud-init 默认走**方式 A**。若想省 API 调用、加快上线，用**方式 B**。

### 方式 A：线上重建（默认，全自动）

cloud-init 已自动执行：

```bash
docker compose -f docker-compose.prod.yml run --rm -e EMBED_BACKEND=api \
  backend python scripts/build_index.py
```

用 SiliconFlow API 编码全部约 1.8 万首（约几百次请求，几分钟）。失败可登录服务器重跑此命令。

### 方式 B：搬运本地已建好的向量（省 API、最快）

本地 Qdrant 数据约 155MB，直接打包传到服务器，免去线上重新编码：

```bash
# 本地（先停本地 qdrant 容器以保证数据一致）
tar -czf qdrant-storage.tgz -C D:/docker-data/qdrant .
scp qdrant-storage.tgz root@<public_ip>:/tmp/

# 服务器上
cd /opt/poem-comunity/deploy
docker compose -f docker-compose.prod.yml stop qdrant
docker run --rm -v deploy_qdrant_storage:/dst -v /tmp:/src alpine \
  sh -c "rm -rf /dst/* && tar -xzf /src/qdrant-storage.tgz -C /dst"
docker compose -f docker-compose.prod.yml start qdrant
```

> 本地用 local 后端、线上用 api 后端，但同为 BGE-M3 + COSINE + L2 归一化，向量空间一致，可直接复用。

## 四、本地手动部署（不用 Terraform，已有服务器时）

```bash
cd deploy
cp .env.prod.example .env        # 填 EMBED_API_KEY、SITE_ADDRESS
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml run --rm backend python scripts/build_index.py
```

## 五、运维常用命令

```bash
cd /opt/poem-comunity/deploy
docker compose -f docker-compose.prod.yml ps         # 状态
docker compose -f docker-compose.prod.yml logs -f    # 日志
docker compose -f docker-compose.prod.yml restart    # 重启
git pull && docker compose -f docker-compose.prod.yml up -d --build   # 更新代码

# 验证向量库
docker compose -f docker-compose.prod.yml exec qdrant \
  wget -qO- http://localhost:6333/collections/poems
```

## 六、安全提示

- `terraform.tfvars`、`deploy/.env` 含密钥，已在 `.gitignore`，**切勿提交**。
- 生产把 `ssh_cidr` 收紧为你的公网 IP（如 `1.2.3.4/32`），别留 `0.0.0.0/0`。
- Qdrant、后端端口**不对外暴露**，仅 Caddy 的 80/443 开放。
- API key 仅存于服务器 `.env`（权限 600），不进镜像、不进 git。

## 七、扩容路线（用得上再看）

当前单机几百人足够。真要扩：先纵向升配 ECS 规格；再不够把 Qdrant 拆到独立实例 / Qdrant Cloud；流量到几千上万并发、需要多副本自动扩缩时，再把这套 compose 迁到阿里云 ACK（Kubernetes）——镜像和架构不用动，只需翻译成 K8s manifest。
