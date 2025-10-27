"use client";
import { useState, FormEvent, useEffect, useRef } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [showLogs, setShowLogs] = useState(false);
  const logSectionRef = useRef<HTMLDivElement | null>(null);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || isSubmitting) return;
    setIsSubmitting(true);

    try {
      const logEntry = `${new Date().toLocaleTimeString()}: "${trimmed}" `;
      console.log(logEntry);
      setLogs((prev) => [...prev, logEntry]);
    } finally {
      setIsSubmitting(false);
    }
  }

  function clearLogs() {
    setLogs([]);
  }

  // When opening logs, scroll down to the log section
  useEffect(() => {
    if (showLogs && logSectionRef.current) {
      logSectionRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [showLogs]);

  return (
    <main className="min-h-svh bg-linear-to-b from-orange-100 via-white to-orange-50 text-zinc-800 flex items-center justify-center p-6 pb-28">
      <div className="w-full max-w-7xl text-center">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-orange-900">Amazon Search</h1>
          <p className="mt-3 text-orange-700 max-w-xl mx-auto font-medium">
            Search your style — discover trends, outfits, and more.
          </p>
        </div>

        {/* Search / Prompt Bar */}
        <form onSubmit={onSubmit} className="max-w-2xl mx-auto ">
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

        {/* Footer copy */}
        <p className="mt-10 text-center text-xs text-orange-600">
          Press <kbd className="rounded border border-orange-300 bg-orange-50 px-1">Enter</kbd> to search • Prototype inspired by Amazon style
        </p>


        {/* Log section in normal flow (hidden until toggled) */}
        {showLogs && (
          <section ref={logSectionRef} className="mt-8 w-full">
            {/* ✅ full width, no max width, no centering */}
            <div className="w-full px-4">
              <div className="bg-white border border-zinc-200 rounded-xl shadow-sm w-full">
                {/* Toolbar */}
                <div className="flex items-center justify-between px-4 py-2 text-xs text-zinc-600">
                  <span className="font-medium">Debug Logs</span>
                  <div className="flex items-center gap-3">
                    <span className="text-zinc-400">{logs.length} entries</span>

                  </div>
                </div>

                {/* ✅ left-aligned logs, full width, scrollable if long */}
                <div className="px-4 pb-4 font-mono text-sm text-zinc-800 text-left whitespace-pre-wrap overflow-y-auto max-h-[70vh] min-h-180 w-full">
                  {logs.length > 0 ? (
                    logs.map((log, i) => (
                      <div
                        key={i}
                        className="py-1 border-b border-zinc-100 last:border-0 wrap-break-word text-left"
                      >
                        {log}
                      </div>
                    ))
                  ) : (
                    <p className="italic text-zinc-400 text-left">No logs yet…</p>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}


      </div>


      {/* Fixed bottom-centered Debug button (not a footer bar) */}
      <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50">
        <button
          onClick={() => setShowLogs((s) => !s)}
          className="px-4 py-2 text-sm font-medium rounded-lg border border-zinc-300 bg-white shadow hover:bg-zinc-50"
        >
          {showLogs ? "Hide Debug Logs" : "Show Debug Logs"}
        </button>
      </div>
    </main>
  );
}
