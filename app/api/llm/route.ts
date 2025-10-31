import { NextRequest, NextResponse } from "next/server";

const BACKEND = process.env.BACKEND_INTERNAL_URL;

/** Type of the expected JSON body */
interface QueryBody {
    user_input?: string;
    q?: string;
    [key: string]: unknown;
}

export async function POST(req: NextRequest) {
    try {
        // Parse body safely
        let body: QueryBody = {};
        try {
            body = (await req.json()) as QueryBody;
        } catch {
            body = {};
        }

        const userInput =
            typeof body.user_input === "string"
                ? body.user_input
                : typeof body.q === "string"
                    ? body.q
                    : null;

        if (!userInput) {
            return NextResponse.json(
                { detail: "Send { user_input: string } or { q: string }" },
                { status: 400 }
            );
        }

        if (BACKEND) {
            try {
                const upstream = await fetch(`${BACKEND}/api/llm_query`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_input: userInput }),
                });

                const contentType =
                    upstream.headers.get("content-type") || "application/json";
                const text = await upstream.text();

                console.log("[/api/llm] proxied →", BACKEND, "status:", upstream.status);

                return new NextResponse(text, {
                    status: upstream.status,
                    headers: { "Content-Type": contentType },
                });
            } catch (proxyErr) {
                const msg =
                    proxyErr instanceof Error ? proxyErr.message : String(proxyErr);
                console.warn("[/api/llm] backend unreachable, falling back:", msg);
            }
        }

        // Stub fallback
        const stub = {
            text: `Stub: received "${userInput}" — backend not connected yet.`,
            links: [],
            debug: { echoed_payload: body },
        };

        console.log("[/api/llm] returning stub for:", userInput);
        return NextResponse.json(stub, { status: 200 });
    } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        return NextResponse.json({ detail: `Route error: ${msg}` }, { status: 500 });
    }
}

export async function GET() {
    return NextResponse.json({ ok: true, route: "/api/llm" });
}
