import type { Poem, SearchResponse } from "./types";

// SSR（服务端）时直连后端容器；客户端用相对路径走自身 /api 代理
// NEXT_PUBLIC_API_BASE 可覆盖（本地开发不设则走 /api）
const BASE =
  process.env.NEXT_PUBLIC_API_BASE ??
  (typeof window === "undefined"
    ? process.env.BACKEND_URL ?? "http://backend:8000"
    : "/api");

export async function searchPoems(query: string, limit = 50, dynasties: string[] = []): Promise<SearchResponse> {
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
  const res = await fetch(`${BASE}/dynasties`, { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}

export async function randomPoems(limit = 6, dynasty?: string): Promise<Poem[]> {
  const url = dynasty
    ? `/api/poems/random?limit=${limit}&dynasty=${encodeURIComponent(dynasty)}`
    : `/api/poems/random?limit=${limit}`;
  const res = await fetch(
    typeof window === "undefined"
      ? `${process.env.BACKEND_URL ?? "http://backend:8000"}/poems/random?limit=${limit}${dynasty ? `&dynasty=${encodeURIComponent(dynasty)}` : ""}`
      : url,
    { cache: "no-store" }
  );
  if (!res.ok) throw new Error(`random poems failed: ${res.status}`);
  return res.json();
}
