import { Suspense } from "react";
import SearchBox from "@/components/SearchBox";
import PoemCard from "@/components/PoemCard";
import { randomPoems, searchPoems, getDynasties } from "@/lib/api";
import type { Poem } from "@/lib/types";

interface Props {
  searchParams: { q?: string; d?: string };
}

async function PoemResults({ query, dynasties }: { query: string; dynasties: string[] }) {
  const { results } = await searchPoems(query, 10, dynasties);
  if (results.length === 0) {
    return <p className="text-center text-gray-500 py-8">未找到相关诗词，换个描述试试</p>;
  }
  return (
    <>
      <p className="text-sm text-gray-500 mb-4">
        &ldquo;{query}&rdquo; 共找到 {results.length} 首
      </p>
      <div className="grid gap-4 sm:grid-cols-2">
        {results.map((poem) => (
          <PoemCard key={poem.id} poem={poem} showScore />
        ))}
      </div>
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
  const selectedDynasties = searchParams.d
    ? searchParams.d.split(",").filter(Boolean)
    : DEFAULT_DYNASTIES;
  const rawDynasties = await getDynasties();
  const allDynasties = [...rawDynasties].sort(
    (a, b) => {
      const ai = DYNASTY_ORDER.indexOf(a);
      const bi = DYNASTY_ORDER.indexOf(b);
      if (ai === -1 && bi === -1) return a.localeCompare(b, "zh");
      if (ai === -1) return 1;
      if (bi === -1) return -1;
      return ai - bi;
    }
  );

  return (
    <main className="min-h-screen px-4 py-12">
      <div className="max-w-3xl mx-auto">
        <header className="text-center mb-10">
          <h1 className="text-3xl font-bold tracking-widest mb-2">找诗诗 🔍</h1>
          <p className="text-sm text-gray-500">用一句话找到若干首懂你的诗</p>
        </header>

        <div className="mb-10">
          <SearchBox defaultValue={query} dynasties={allDynasties} selected={selectedDynasties} />
        </div>

        <section>
          {query ? (
            <Suspense
              fallback={
                <p className="text-center text-gray-400 py-8">正在寻诗……</p>
              }
            >
              <PoemResults query={query} dynasties={selectedDynasties} />
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
