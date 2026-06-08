"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

interface Props {
  defaultValue?: string;
  dynasties?: string[];
  selected?: string[];
}

export default function SearchBox({ defaultValue = "", dynasties = [], selected = [] }: Props) {
  const router = useRouter();
  const [value, setValue] = useState(defaultValue);
  const [checked, setChecked] = useState<Set<string>>(new Set(selected));

  function toggleDynasty(d: string) {
    setChecked((prev) => {
      const next = new Set(prev);
      next.has(d) ? next.delete(d) : next.add(d);
      return next;
    });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = value.trim();
    if (!q) return;
    const params = new URLSearchParams({ q });
    if (checked.size > 0) params.set("d", [...checked].join(","));
    router.push(`/?${params.toString()}`);
  }

  return (
    <div className="max-w-xl mx-auto">
      <form onSubmit={handleSubmit} className="flex gap-2 w-full">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="用心情、意境、主题来寻诗……"
          className="flex-1 px-4 py-3 rounded-lg border border-[color:var(--paper-dark)] bg-white/70 focus:outline-none focus:ring-2 focus:ring-[color:var(--accent)] focus:ring-opacity-40 text-base"
          aria-label="诗词搜索"
        />
        <button
          type="submit"
          className="px-6 py-3 rounded-lg bg-[color:var(--accent)] text-white font-medium hover:opacity-90 transition-opacity"
        >
          寻诗
        </button>
      </form>

      {dynasties.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3 justify-center">
          {dynasties.map((d) => (
            <label
              key={d}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-sm cursor-pointer select-none transition-colors ${
                checked.has(d)
                  ? "bg-[color:var(--accent)] border-[color:var(--accent)] text-white"
                  : "border-[color:var(--paper-dark)] text-gray-600 hover:border-[color:var(--accent)]"
              }`}
            >
              <input
                type="checkbox"
                className="sr-only"
                checked={checked.has(d)}
                onChange={() => toggleDynasty(d)}
              />
              {d}
            </label>
          ))}
          {checked.size > 0 && (
            <button
              type="button"
              onClick={() => setChecked(new Set())}
              className="px-3 py-1 rounded-full text-sm text-gray-400 hover:text-gray-600 transition-colors"
            >
              清除筛选
            </button>
          )}
        </div>
      )}
    </div>
  );
}
