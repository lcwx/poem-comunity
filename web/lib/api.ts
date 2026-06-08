import type { Poem, SearchResponse } from "./types";

// 服务端渲染时需要绝对 URL，客户端可用相对路径
const BASE =
  process.env.NEXT_PUBLIC_API_BASE ??
  (typeof window === "undefined" ? "http://localhost:3000/api" : "/api");

export async function searchPoems(query: string, limit = 10, dynasties: string[] = []): Promise<SearchResponse> {
  const res = await fetch(`${BASE}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, limit, dynasties }),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`search failed: ${res.status}`);
  return res.json();
}

export async function getPoem(id: string): Promise<Poem> {
  const res = await fetch(`${BASE}/poem/${encodeURIComponent(id)}`, {
    cache: "force-cache",
  });
  if (!res.ok) throw new Error(`poem not found: ${id}`);
  return res.json();
}

export async function getDynasties(): Promise<string[]> {
  const res = await fetch(`${BASE}/dynasties`, { cache: "force-cache" });
  if (!res.ok) return [];
  return res.json();
}

export async function randomPoems(limit = 6): Promise<Poem[]> {
  const res = await fetch(`${BASE}/poems/random?limit=${limit}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`random poems failed: ${res.status}`);
  return res.json();
}
