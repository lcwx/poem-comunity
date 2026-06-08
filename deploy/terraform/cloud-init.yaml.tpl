#cloud-config
# 首次开机自动部署 poem-comunity。
# 变量由 Terraform templatefile 注入；$$ 为转义后的真实 shell $。
package_update: true

write_files:
  - path: /opt/deploy.sh
    permissions: "0755"
    content: |
      #!/usr/bin/env bash
      set -euo pipefail
      exec > /var/log/poem-deploy.log 2>&1
      echo "=== [$(date)] 开始部署 ==="

      # 1. 安装 Docker + compose 插件
      curl -fsSL https://get.docker.com | sh
      systemctl enable --now docker

      # 2. 拉代码
      APP_DIR=/opt/poem-comunity
      rm -rf "$APP_DIR"
      git clone --branch "${repo_branch}" --depth 1 "${repo_url}" "$APP_DIR"
      cd "$APP_DIR/deploy"

      # 3. 写生产 .env（compose 同目录自动读取）
      cat > .env <<ENVEOF
      EMBED_API_KEY=${embed_api_key}
      EMBED_API_BASE=https://api.siliconflow.cn/v1
      EMBED_API_MODEL=BAAI/bge-m3
      SITE_ADDRESS=${site_address}
      ENVEOF
      chmod 600 .env

      # 4. 构建并启动
      docker compose -f docker-compose.prod.yml up -d --build

      # 5. 等 Qdrant 就绪后建索引（API 后端编码全部语料）
      echo "=== 等待服务就绪 ==="
      sleep 30
      docker compose -f docker-compose.prod.yml run --rm \
        -e EMBED_BACKEND=api \
        backend python scripts/build_index.py || echo "建索引失败，请登录手动重试"

      echo "=== [$(date)] 部署完成 ==="

runcmd:
  - [bash, /opt/deploy.sh]
