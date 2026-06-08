import Link from "next/link";
import type { Poem } from "@/lib/types";

interface Props {
  poem: Poem;
  showScore?: boolean;
}

export default function PoemCard({ poem, showScore }: Props) {
  return (
    <Link
      href={`/poem/${poem.id}`}
      className="block bg-white/60 hover:bg-white/90 border border-[color:var(--paper-dark)] rounded-lg p-5 transition-colors group"
    >
      <div className="flex items-baseline justify-between mb-2">
        <h2 className="text-lg font-semibold group-hover:text-[color:var(--accent)] transition-colors">
          {poem.title}
        </h2>
        <span className="text-sm text-gray-500 ml-3 shrink-0">
          {poem.dynasty}・{poem.author}
        </span>
      </div>
      <div className="text-sm text-gray-700 leading-7 line-clamp-3">
        {poem.content.map((line, i) => (
          <span key={i}>
            {line}
            {i < poem.content.length - 1 && <br />}
          </span>
        ))}
      </div>
      {showScore && poem.score !== undefined && (
        <div className="mt-2 text-xs text-gray-400">
          相关度 {(poem.score * 100).toFixed(1)}%
        </div>
      )}
    </Link>
  );
}
