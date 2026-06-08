import { notFound } from "next/navigation";
import { getPoem } from "@/lib/api";
import BackButton from "@/components/BackButton";

interface Props {
  params: { id: string };
}

export async function generateMetadata({ params }: Props) {
  try {
    const poem = await getPoem(params.id);
    return { title: `${poem.title} · ${poem.author} · 诗社` };
  } catch {
    return { title: "诗词 · 诗社" };
  }
}

export default async function PoemPage({ params }: Props) {
  let poem;
  try {
    poem = await getPoem(params.id);
  } catch {
    notFound();
  }

  return (
    <main className="min-h-screen px-4 py-12">
      <div className="max-w-xl mx-auto">
        <BackButton />

        <article className="bg-white/60 rounded-xl p-8 border border-[color:var(--paper-dark)]">
          <h1 className="text-2xl font-bold tracking-wider mb-1">{poem.title}</h1>
          <p className="text-sm text-gray-500 mb-8">
            {poem.dynasty}・{poem.author}
          </p>

          <div className="leading-10 text-lg tracking-widest space-y-1">
            {poem.content.map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
        </article>
      </div>
    </main>
  );
}
