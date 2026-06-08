import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "诗社 · 语义诗词检索",
  description: "用自然语言检索古典诗词，感受文字之美",
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
