"use client";
import { useState, FormEvent } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || isSubmitting) return;
    setIsSubmitting(true);

    try {
      console.log("User query:", trimmed);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-svh bg-gradient-to-b from-orange-100 via-white to-orange-50 text-zinc-800 flex items-center justify-center p-6">
      <div className="w-full max-w-2xl text-center">
        {/* Header */}
        <div className="mb-8">
          
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-orange-900">Amazon Search</h1>
          <p className="mt-3 text-orange-700 max-w-xl mx-auto font-medium">
            Search your style — discover trends, outfits, and more.
          </p>
        </div>

        {/* Search / Prompt Bar */}
        <form onSubmit={onSubmit} className="relative">
          <div className="group rounded-2xl bg-white shadow-lg ring-1 ring-orange-200 hover:ring-orange-300 focus-within:ring-orange-400 transition-all">
            <div className="flex items-center gap-2 px-4 md:px-5">
              <svg
                aria-hidden
                viewBox="0 0 24 24"
                className="h-5 w-5 shrink-0 text-orange-500 group-focus-within:text-orange-600"
              >
                <path
                  fill="currentColor"
                  d="M10 2a8 8 0 105.293 14.293l3.707 3.707 1.414-1.414-3.707-3.707A8 8 0 0010 2zm0 2a6 6 0 110 12A6 6 0 0110 4z"
                />
              </svg>
              <input
                autoFocus
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search for fashion, accessories, or brands…"
                className="w-full bg-transparent outline-none placeholder:text-orange-400 text-base md:text-lg py-4 md:py-5 text-orange-900"
                aria-label="Search Amazon style"
              />
              <button
                type="submit"
                disabled={!query.trim() || isSubmitting}
                className="ml-2 my-2 inline-flex items-center justify-center rounded-xl border border-orange-300 bg-orange-500 px-4 py-2 text-sm font-medium text-white hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? "Searching…" : "Search"}
              </button>
            </div>
          </div>
        </form>


        {/* Footer */}
        <p className="mt-10 text-center text-xs text-orange-600">
          Press <kbd className="rounded border border-orange-300 bg-orange-50 px-1">Enter</kbd> to search • Prototype inspired by Amazon style
        </p>
      </div>
    </main>
  );
}
