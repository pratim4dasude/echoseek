// "use client";
// import { useState, FormEvent, useEffect, useRef } from "react";

// import { RecommendResponse } from "./types";
// import ProductCard from "./components/ProductCard";

// // --- Temporary mock until your backend is ready ---
// function mockResponse(query: string): RecommendResponse {
//   return {
//     text: `For "${query}", these outfits are trending on Amazon right now.`,
//     links: [
//       {
//         id: "1",
//         title: "Slim Fit Blue Jeans for Men",
//         url: "https://www.amazon.in/Peter-England-Striped-Shirt-PCSFSSLPA19862_Pink/dp/B0F9DYTWW7/?_encoding=UTF8&ref_=pd_hp_d_btf_ci_mcx_mr_ca_id_hp_d&psc=1",
//         image:
//           "https://m.media-amazon.com/images/I/71AJio3+JQL._SY550_.jpg",
//         price: "₹1,499",
//         rating: 4.2,
//       },
//       {
//         id: "2",
//         title: "Classic Black Pants",
//         url: "https://www.amazon.in/dp/B0CXYZ5678",
//         image:
//           "https://m.media-amazon.com/images/I/61uKxD1V5eL._AC_UL480_FMwebp_QL65_.jpg",
//         price: "₹1,299",
//         rating: 4.4,
//       },
//       {
//         id: "3",
//         title: "Party Wear Denim Jeans",
//         url: "https://www.amazon.in/dp/B0B4ABC999",
//         image:
//           "https://m.media-amazon.com/images/I/71X9RrQPVnL._AC_UL480_FMwebp_QL65_.jpg",
//         price: "₹1,899",
//         rating: 4.1,
//       },
//       {
//         id: "4",
//         title: "Men’s Tapered Chinos",
//         url: "https://www.amazon.in/dp/B0B2CDE123",
//         image:
//           "https://m.media-amazon.com/images/I/61otbq5F7xL._AC_UL480_FMwebp_QL65_.jpg",
//         price: "₹1,199",
//         rating: 4.0,
//       },
//       {
//         id: "5",
//         title: "Casual Cotton Pants",
//         url: "https://www.amazon.in/dp/B09FABC890",
//         image:
//           "https://m.media-amazon.com/images/I/71DnDx1yQBL._AC_UL480_FMwebp_QL65_.jpg",
//         price: "₹999",
//         rating: 4.3,
//       },
//     ],
//   };
// }
// // ---------------------------------------------------

// export default function Home() {
//   const [query, setQuery] = useState("");
//   const [isSubmitting, setIsSubmitting] = useState(false);
//   const [logs, setLogs] = useState<string[]>([]);
//   const [showLogs, setShowLogs] = useState(false);
//   const [result, setResult] = useState<RecommendResponse | null>(null); // ✅ correct type
//   const [error, setError] = useState<string | null>(null);
//   const logSectionRef = useRef<HTMLDivElement | null>(null);

//   async function onSubmit(e: FormEvent<HTMLFormElement>) {
//     e.preventDefault();
//     const trimmed = query.trim();
//     if (!trimmed || isSubmitting) return;

//     setIsSubmitting(true);
//     setError(null);
//     setResult(null);

//     try {
//       // Optional log line (kept your style)
//       const logEntry = `${new Date().toLocaleTimeString()}: "${trimmed}"`;
//       setLogs((prev) => [...prev, logEntry]);

//       // ⬇️ Use mock for now; swap to real backend later
//       const json = mockResponse(trimmed);
//       setResult(json);
//       setLogs((prev) => [...prev, `Response: ${JSON.stringify(json)}`]);

//       // When backend ready:
//       // const res = await fetch("/api/recommend", {
//       //   method: "POST",
//       //   headers: { "content-type": "application/json" },
//       //   body: JSON.stringify({ q: trimmed }),
//       // });
//       // if (!res.ok) throw new Error(`HTTP ${res.status}`);
//       // const json: RecommendResponse = await res.json();
//       // setResult(json);
//     } catch (err) {
//       if (err instanceof Error) {
//         setError(err.message);
//         console.error(err.message);
//       } else {
//         setError("Something went wrong");
//         console.error(err);
//       }
//     } finally {
//       setIsSubmitting(false);
//     }
//   }

//   function clearLogs() {
//     setLogs([]);
//   }

//   // When opening logs, scroll down to the log section
//   useEffect(() => {
//     if (showLogs && logSectionRef.current) {
//       logSectionRef.current.scrollIntoView({
//         behavior: "smooth",
//         block: "start",
//       });
//     }
//   }, [showLogs]);

//   return (
//     <main className="min-h-svh bg-linear-to-b from-orange-100 via-white to-orange-50 text-zinc-800 flex items-center justify-center p-6 pb-28">
//       <div className="w-full max-w-7xl text-center">
//         {/* Header */}
//         <div className="mb-8">
//           <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-orange-900">
//             Amazon Search
//           </h1>
//           <p className="mt-3 text-orange-700 max-w-xl mx-auto font-medium">
//             Search your style — discover trends, outfits, and more.
//           </p>
//         </div>

//         {/* Search / Prompt Bar */}
//         <form onSubmit={onSubmit} className="max-w-2xl mx-auto ">
//           <div className="group rounded-2xl bg-white shadow-lg ring-1 ring-orange-200 hover:ring-orange-300 focus-within:ring-orange-400 transition-all">
//             <div className="flex items-center gap-2 px-4 md:px-5">
//               <svg
//                 aria-hidden
//                 viewBox="0 0 24 24"
//                 className="h-5 w-5 shrink-0 text-orange-500 group-focus-within:text-orange-600"
//               >
//                 <path
//                   fill="currentColor"
//                   d="M10 2a8 8 0 105.293 14.293l3.707 3.707 1.414-1.414-3.707-3.707A8 8 0 0010 2zm0 2a6 6 0 110 12A6 6 0 0110 4z"
//                 />
//               </svg>
//               <input
//                 autoFocus
//                 type="text"
//                 value={query}
//                 onChange={(e) => setQuery(e.target.value)}
//                 placeholder="Search for fashion, accessories, or brands…"
//                 className="w-full bg-transparent outline-none placeholder:text-orange-400 text-base md:text-lg py-4 md:py-5 text-orange-900"
//                 aria-label="Search Amazon style"
//               />
//               <button
//                 type="submit"
//                 disabled={!query.trim() || isSubmitting}
//                 className="ml-2 my-2 inline-flex items-center justify-center rounded-xl border border-orange-300 bg-orange-500 px-4 py-2 text-sm font-medium text-white hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
//               >
//                 {isSubmitting ? "Searching…" : "Search"}
//               </button>
//             </div>
//           </div>
//         </form>

//         {/* Error */}
//         {error && (
//           <div className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3 mb-6">
//             {error}
//           </div>
//         )}

//         {/* Response */}
//         {result && (
//           <div className="mt-8 text-left space-y-8">
//             {/* Query */}
//             <div className="rounded-xl bg-white p-4 shadow border border-zinc-200">
//               <div className="text-xs text-zinc-500 mb-1">Your query</div>
//               <div className="font-medium text-zinc-800">{query}</div>
//             </div>

//             {/* Response Text */}
//             <div className="rounded-xl bg-orange-50 p-4 shadow border border-orange-200">
//               <div className="text-xs text-orange-700 mb-1">Recommendation</div>
//               <p className="text-zinc-900">{result.text}</p>
//             </div>

//             {/* Product Grid */}
//             <section>
//               <div className="flex items-center justify-between mb-3">
//                 <h2 className="text-lg font-semibold text-zinc-900">
//                   Top Picks from Amazon
//                 </h2>
//                 <span className="text-xs text-zinc-500">
//                   {result.links.length} items
//                 </span>
//               </div>
//               <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
//                 {result.links.map((item) => (
//                   <ProductCard key={item.id} item={item} />
//                 ))}
//               </div>
//             </section>
//           </div>
//         )}

//         {/* Footer copy */}
//         <p className="mt-10 text-center text-xs text-orange-600">
//           Press <kbd className="rounded border border-orange-300 bg-orange-50 px-1">Enter</kbd> to search • Prototype inspired by Amazon style
//         </p>

//         {/* Log section (toggle) */}
//         {showLogs && (
//           <section ref={logSectionRef} className="mt-8 w-full">
//             <div className="w-full px-4">
//               <div className="bg-white border border-zinc-200 rounded-xl shadow-sm w-full">
//                 {/* Toolbar */}
//                 <div className="flex items-center justify-between px-4 py-2 text-xs text-zinc-600">
//                   <span className="font-medium">Debug Logs</span>
//                   <div className="flex items-center gap-3">
//                     <span className="text-zinc-400">{logs.length} entries</span>
//                     <button
//                       onClick={clearLogs}
//                       className="px-2 py-1 rounded border border-zinc-300 hover:bg-zinc-50"
//                     >
//                       Clear
//                     </button>
//                   </div>
//                 </div>

//                 {/* Logs */}
//                 <div className="px-4 pb-4 font-mono text-sm text-zinc-800 text-left whitespace-pre-wrap overflow-y-auto max-h-[70vh] min-h-180 w-full">
//                   {logs.length > 0 ? (
//                     logs.map((log, i) => (
//                       <div
//                         key={i}
//                         className="py-1 border-b border-zinc-100 last:border-0 wrap-break-word text-left"
//                       >
//                         {log}
//                       </div>
//                     ))
//                   ) : (
//                     <p className="italic text-zinc-400 text-left">No logs yet…</p>
//                   )}
//                 </div>
//               </div>
//             </div>
//           </section>
//         )}
//       </div>

//       {/* Fixed bottom-centered Debug button */}
//       <div className="fixed bottom-4 left-4 z-50">
//         <button
//           onClick={() => setShowLogs((s) => !s)}
//           className="px-4 py-2 text-sm font-medium rounded-lg border border-zinc-300 bg-white shadow hover:bg-zinc-50"
//         >
//           {showLogs ? "Hide Debug Logs" : "Show Debug Logs"}
//         </button>
//       </div>
//     </main>
//   );
// }


"use client";
import { useState, FormEvent, useEffect, useRef } from "react";
import { RecommendResponse } from "./types";
import ProductCard from "./components/ProductCard";

// --- Temporary mock until your backend is ready ---
function mockResponse(query: string): RecommendResponse {
  return {
    text: `For "${query}", these outfits are trending on Amazon right now.`,
    links: [
      {
        id: "1",
        title: "Slim Fit Blue Jeans for Men",
        url: "https://www.amazon.in/Peter-England-Striped-Shirt-PCSFSSLPA19862_Pink/dp/B0F9DYTWW7/?_encoding=UTF8&ref_=pd_hp_d_btf_ci_mcx_mr_ca_id_hp_d&psc=1",
        image: "https://m.media-amazon.com/images/I/71AJio3+JQL._SY550_.jpg",
        price: "₹1,499",
        rating: 4.2,
      },
      {
        id: "2",
        title: "Classic Black Pants",
        url: "https://www.amazon.in/dp/B0CXYZ5678",
        image: "https://m.media-amazon.com/images/I/61uKxD1V5eL._AC_UL480_FMwebp_QL65_.jpg",
        price: "₹1,299",
        rating: 4.4,
      },
      {
        id: "3",
        title: "Party Wear Denim Jeans",
        url: "https://www.amazon.in/dp/B0B4ABC999",
        image: "https://m.media-amazon.com/images/I/71X9RrQPVnL._AC_UL480_FMwebp_QL65_.jpg",
        price: "₹1,899",
        rating: 4.1,
      },
      {
        id: "4",
        title: "Men’s Tapered Chinos",
        url: "https://www.amazon.in/dp/B0B2CDE123",
        image: "https://m.media-amazon.com/images/I/61otbq5F7xL._AC_UL480_FMwebp_QL65_.jpg",
        price: "₹1,199",
        rating: 4.0,
      },
      {
        id: "5",
        title: "Casual Cotton Pants",
        url: "https://www.amazon.in/dp/B09FABC890",
        image: "https://m.media-amazon.com/images/I/71DnDx1yQBL._AC_UL480_FMwebp_QL65_.jpg",
        price: "₹999",
        rating: 4.3,
      },
    ],
  };
}

// --- Reusable Search Bar Component ---
function SearchBar({
  query,
  setQuery,
  isSubmitting,
  onSubmit,
}: {
  query: string;
  setQuery: (v: string) => void;
  isSubmitting: boolean;
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
}) {
  return (
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
  );
}

// --- Page Component ---
export default function Home() {
  const [query, setQuery] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [showLogs, setShowLogs] = useState(false);
  const [result, setResult] = useState<RecommendResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const logSectionRef = useRef<HTMLDivElement | null>(null);

  const docked = !!result; // true after first result (moves search bar down)

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || isSubmitting) return;

    setIsSubmitting(true);
    setError(null);
    setResult(null);

    try {
      const logEntry = `${new Date().toLocaleTimeString()}: "${trimmed}"`;
      setLogs((prev) => [...prev, logEntry]);

      const json = mockResponse(trimmed);
      setResult(json);
      setLogs((prev) => [...prev, `Response: ${JSON.stringify(json)}`]);
    } catch (err) {
      if (err instanceof Error) setError(err.message);
      else setError("Something went wrong");
    } finally {
      setIsSubmitting(false);
    }
  }

  useEffect(() => {
    if (showLogs && logSectionRef.current) {
      logSectionRef.current.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  }, [showLogs]);

  return (
    <main
      className={`min-h-svh bg-linear-to-b from-orange-100 via-white to-orange-50 text-zinc-800 flex flex-col items-center justify-start p-6 ${docked ? "pb-40" : "pb-28"
        }`}
    >
      <div className="w-full max-w-7xl text-center">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-orange-900">
            Amazon Search
          </h1>
          <p className="mt-3 text-orange-700 max-w-xl mx-auto font-medium">
            Search your style — discover trends, outfits, and more.
          </p>
        </div>

        {/* Search bar position */}
        {!docked && (
          <SearchBar
            query={query}
            setQuery={setQuery}
            isSubmitting={isSubmitting}
            onSubmit={onSubmit}
          />
        )}

        {/* Error */}
        {error && (
          <div className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3 mb-6">
            {error}
          </div>
        )}

        {/* Response section */}
        {result && (
          <div className="mt-8 text-left space-y-8">
            {/* Query */}
            <div className="rounded-xl bg-white p-4 shadow border border-zinc-200">
              <div className="text-xs text-zinc-500 mb-1">Your query</div>
              <div className="font-medium text-zinc-800">{query}</div>
            </div>

            {/* Recommendation */}
            <div className="rounded-xl bg-orange-50 p-4 shadow border border-orange-200">
              <div className="text-xs text-orange-700 mb-1">Recommendation</div>
              <p className="text-zinc-900">{result.text}</p>
            </div>

            {/* Product grid */}
            <section>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-lg font-semibold text-zinc-900">
                  Top Picks from Amazon
                </h2>
                <span className="text-xs text-zinc-500">
                  {result.links.length} items
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
                {result.links.map((item) => (
                  <ProductCard key={item.id} item={item} />
                ))}
              </div>
            </section>
          </div>
        )}

        {/* Footer note */}
        <p className="mt-10 text-center text-xs text-orange-600">
          Press{" "}
          <kbd className="rounded border border-orange-300 bg-orange-50 px-1">
            Enter
          </kbd>{" "}
          to search • Prototype inspired by Amazon style
        </p>

        {/* Logs section */}
        {showLogs && (
          <section ref={logSectionRef} className="mt-8 w-full">
            <div className="w-full px-4">
              <div className="bg-white border border-zinc-200 rounded-xl shadow-sm w-full">
                <div className="flex items-center justify-between px-4 py-2 text-xs text-zinc-600">
                  <span className="font-medium">Debug Logs</span>
                  <div className="flex items-center gap-3">
                    <span className="text-zinc-400">{logs.length} entries</span>
                    <button
                      onClick={() => setLogs([])}
                      className="px-2 py-1 rounded border border-zinc-300 hover:bg-zinc-50"
                    >
                      Clear
                    </button>
                  </div>
                </div>

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
                    <p className="italic text-zinc-400 text-left">
                      No logs yet…
                    </p>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}
      </div>

      {/* Debug toggle (left) */}
      <div className="fixed bottom-4 left-4 z-50">
        <button
          onClick={() => setShowLogs((s) => !s)}
          className="px-4 py-2 text-sm font-medium rounded-lg border border-zinc-300 bg-white shadow hover:bg-zinc-50"
        >
          {showLogs ? "Hide Debug Logs" : "Show Debug Logs"}
        </button>
      </div>

      {/* Docked search bar after response */}
      {docked && (
        <div className="fixed bottom-0 left-0 right-0 z-40">
          <div className="max-w-2xl mx-auto p-3">
            <SearchBar
              query={query}
              setQuery={setQuery}
              isSubmitting={isSubmitting}
              onSubmit={onSubmit}
            />
          </div>
        </div>
      )}
    </main>
  );
}
