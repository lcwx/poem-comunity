/** @type {import('next').NextConfig} */
const nextConfig = {
  // 生产容器用 standalone 产物，镜像更小；不影响本地 dev
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.BACKEND_URL ?? "http://localhost:8000"}/:path*`,
      },
    ];
  },
};

export default nextConfig;
