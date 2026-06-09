/** @type {import('next').NextConfig} */
const nextConfig = {
  // 生产容器用 standalone 产物，镜像更小；不影响本地 dev
  output: "standalone",
};

export default nextConfig;
