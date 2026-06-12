import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "找诗诗 · 语义式搜索古诗词",
  description: "别背诗了，跟找诗诗说说你的心情，它来找诗",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">{children}</body>
    </html>
  );
}
