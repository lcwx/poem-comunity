"use client";

import { useRouter } from "next/navigation";

export default function BackButton() {
  const router = useRouter();
  return (
    <button
      onClick={() => router.back()}
      className="text-sm text-gray-400 hover:text-gray-600 mb-8 inline-block cursor-pointer"
    >
      ← 返回
    </button>
  );
}
