import { Suspense } from "react";
import Link from "next/link";
import SearchBox from "@/components/SearchBox";
import PoemCard from "@/components/PoemCard";
import { randomPoems, searchPoems, getDynasties } from "@/lib/api";
import type { Poem } from "@/lib/types";

interface Props {
  searchParams: { q?: string; d?: string; page?: string };
}

const PAGE_SIZE = 10;

async function PoemResults({
  query,
  dynasties,
  page,
}: {
  query: string;
  dynasties: string[];
  page: number;
}) {
  const { results } = await searchPoems(query, 50, dynasties);
  if (results.length === 0) {
    return <p className="text-center text-gray-500 py-8">未找到相关诗词，换个描述试试</p>;
  }

  const totalPages = Math.ceil(results.length / PAGE_SIZE);
  const safePage = Math.min(Math.max(1, page), totalPages);
  const pagePoems = results.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);

  function pageUrl(p: number, q: string, d: string[]) {
    const params = new URLSearchParams({ q });
    if (d.length > 0) params.set("d", d.join(","));
    if (p > 1) params.set("page", String(p));
    return `/?${params.toString()}`;
  }

  return (
    <>
      <p className="text-sm text-gray-500 mb-4">
        &ldquo;{query}&rdquo; 共找到 {results.length} 首 · 第 {safePage}/{totalPages} 页
      </p>
      <div className="grid gap-4 sm:grid-cols-2">
        {pagePoems.map((poem) => (
          <PoemCard key={poem.id} poem={poem} showScore />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex justify-center gap-2 mt-8">
          {safePage > 1 && (
            <Link
              href={pageUrl(safePage - 1, query, dynasties)}
              className="px-4 py-2 rounded-lg border border-[color:var(--paper-dark)] text-sm hover:border-[color:var(--accent)] transition-colors"
            >
              ← 上一页
            </Link>
          )}
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
            <Link
              key={p}
              href={pageUrl(p, query, dynasties)}
              className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                p === safePage
                  ? "bg-[color:var(--accent)] text-white"
                  : "border border-[color:var(--paper-dark)] hover:border-[color:var(--accent)]"
              }`}
            >
              {p}
            </Link>
          ))}
          {safePage < totalPages && (
            <Link
              href={pageUrl(safePage + 1, query, dynasties)}
              className="px-4 py-2 rounded-lg border border-[color:var(--paper-dark)] text-sm hover:border-[color:var(--accent)] transition-colors"
            >
              下一页 →
            </Link>
          )}
        </div>
      )}
    </>
  );
}

async function RandomPoems() {
  let poems: Poem[] = [];
  try {
    poems = await randomPoems(6);
  } catch {
    return null;
  }
  if (poems.length === 0) return null;
  return (
    <>
      <h2 className="text-base text-gray-500 mb-4 text-center">今日推荐</h2>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {poems.map((poem) => (
          <PoemCard key={poem.id} poem={poem} />
        ))}
      </div>
    </>
  );
}

const DYNASTY_ORDER = ["楚辞", "诗经", "唐", "宋词", "元", "现代"];
const DEFAULT_DYNASTIES = ["楚辞", "诗经", "唐", "宋词"];

export default async function Home({ searchParams }: Props) {
  const query = searchParams.q?.trim() ?? "";
  const page = parseInt(searchParams.page ?? "1", 10);
  const selectedDynasties = searchParams.d
    ? searchParams.d.split(",").filter(Boolean)
    : DEFAULT_DYNASTIES;
  const rawDynasties = await getDynasties();
  const allDynasties = [...rawDynasties].sort((a, b) => {
    const ai = DYNASTY_ORDER.indexOf(a);
    const bi = DYNASTY_ORDER.indexOf(b);
    if (ai === -1 && bi === -1) return a.localeCompare(b, "zh");
    if (ai === -1) return 1;
    if (bi === -1) return -1;
    return ai - bi;
  });

  return (
    <main className="min-h-screen px-4 py-12">
      <div className="max-w-3xl mx-auto">
        <header className="text-center mb-10">
          <h1 className="text-3xl font-bold tracking-widest mb-2">找诗诗 🔍</h1>
          <p className="text-sm text-gray-500">AI语义搜索古诗词</p>
        </header>

        <div className="mb-10">
          <SearchBox defaultValue={query} dynasties={allDynasties} selected={selectedDynasties} />
        </div>

        <section>
          {query ? (
            <Suspense fallback={<p className="text-center text-gray-400 py-8">正在寻诗……</p>}>
              <PoemResults query={query} dynasties={selectedDynasties} page={page} />
            </Suspense>
          ) : (
            <Suspense fallback={null}>
              <RandomPoems />
            </Suspense>
          )}
        </section>
      </div>
    </main>
  );
}
