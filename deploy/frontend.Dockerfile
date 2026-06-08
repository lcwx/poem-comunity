# 前端镜像：多阶段构建，Next.js standalone 产物。
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
# standalone 自带最小 node_modules 和 server.js
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
# server.js 由 standalone 产出；BACKEND_URL 运行时由 compose 注入
CMD ["node", "server.js"]
