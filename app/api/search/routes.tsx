import { NextResponse } from "next/server";

// POST /api/search  — handles search requests
export async function POST(req: Request) {
    console.log("[/api/search] POST hit");
    try {
        const { q } = await req.json();
        const query = String(q || "").trim();

        // simulate a short delay (optional)
        await new Promise((r) => setTimeout(r, 250));

        if (!query) {
            return NextResponse.json({ items: [] });
        }

        // mock data (replace later with your real backend call)
        const items = Array.from({ length: 6 }).map((_, i) => ({
            id: `${encodeURIComponent(query)}-${i + 1}`,
            title: `${query} — Product ${i + 1}`,
            url: `https://example.com/search?q=${encodeURIComponent(query)}&item=${i + 1}`,
            price: i % 2 === 0 ? `₹${(999 + i * 123).toLocaleString("en-IN")}` : undefined,
            description:
                i % 2 === 0
                    ? `Top-rated ${query} with fast delivery and easy returns. Highly reviewed by customers.`
                    : `Discover styles related to "${query}" across fashion, accessories and more.`,
        }));

        return NextResponse.json({ items });
    } catch (err: any) {
        return new NextResponse(`Bad Request: ${String(err?.message || err)}`, { status: 400 });
    }
}

// (optional) quick GET health check
export async function GET() {
    return NextResponse.json({ ok: true, service: "mock-search", ts: Date.now() });
}
