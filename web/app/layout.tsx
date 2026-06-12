import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "找诗诗 · AI语义搜索古诗词",
  description: "AI语义搜索古诗词",
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
