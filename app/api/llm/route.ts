import { NextRequest, NextResponse } from "next/server";

const LONG_TIMEOUT_MS = 600000;
const DEFAULT_BACKEND_URL = "http://localhost:8000";
const MAX_RETRIES = 100000;
const RETRY_DELAY_MS = 10000; 

interface QueryBody {
    user_input?: string;
    q?: string;
    [key: string]: unknown;
}


export async function POST(req: NextRequest) {
    
    const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || DEFAULT_BACKEND_URL;

    try {
        let body: QueryBody = {};
        try { body = (await req.json()) as QueryBody; } catch { body = {}; }
        const userInput = typeof body.user_input === "string" ? body.user_input : typeof body.q === "string" ? body.q : null;

        if (!userInput) {
            return NextResponse.json({ detail: "Send { user_input: string } or { q: string }" }, { status: 400 });
        }

        if (!BACKEND_URL || BACKEND_URL === 'undefined') {
            console.warn("[/api/llm] Backend URL not configured, returning stub.");
        }

        let upstream: Response | null = null;
        let lastError: string | null = null;
        let attempt = 0;

        while (attempt < MAX_RETRIES) {
            attempt++;

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), LONG_TIMEOUT_MS);

            try {
                console.log(`----> [/api/llm] Attempt ${attempt}/${MAX_RETRIES}: Proxying query to: ${BACKEND_URL}`);

                upstream = await fetch(`${BACKEND_URL}/api/llm_query`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_input: userInput }),
                    signal: controller.signal,
                });

                clearTimeout(timeoutId);

                if (upstream) break;

            } catch (proxyErr) {
                clearTimeout(timeoutId);
                const msg = proxyErr instanceof Error ? proxyErr.message : String(proxyErr);
                lastError = msg;

                if (msg.includes('abort') || msg.includes('timeout')) {
                    console.warn(`[/api/llm] Attempt ${attempt} timed out after ${LONG_TIMEOUT_MS / 1000}s. No further retries on hard timeout.`);
                    
                    attempt = MAX_RETRIES; 
                    break;
                }

                // RETRY
                if (msg.includes('fetch failed') || msg.includes('ECONNREFUSED')) {
                    console.warn(`[/api/llm] Attempt ${attempt} failed due to network error. Retrying in ${RETRY_DELAY_MS}ms...`);
                    if (attempt < MAX_RETRIES) {
                        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY_MS));
                    }
                } else {
                    
                    console.error(`[/api/llm] Unexpected error on attempt ${attempt}: ${msg}`);
                    attempt = MAX_RETRIES; 
                    break;
                }
            }
        }

        if (upstream && upstream.ok) {
            const contentType = upstream.headers.get("content-type") || "application/json";
            const text = await upstream.text();

            console.log("[/api/llm] FINAL SUCCESS - proxied →", BACKEND_URL, "status:", upstream.status);

            return new NextResponse(text, {
                status: upstream.status,
                headers: { "Content-Type": contentType },
            });
        }
        // Timeouts 
        if (lastError && lastError.includes('abort') || lastError?.includes('timeout')) {
            return NextResponse.json({ detail: "LLM request timed out on proxy side." }, { status: 504 });
        }

        
        const stub = {
            text: `Stub: received "${userInput}" — backend not connected after ${MAX_RETRIES} tries.`,
            links: [],
            debug: { echoed_payload: body, last_error: lastError },
        };

        console.log("[/api/llm] returning stub fallback for:", userInput);
        return NextResponse.json(stub, { status: 200 });

    } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        return NextResponse.json({ detail: `Route error: ${msg}` }, { status: 500 });
    }
}


export async function GET() {
    return NextResponse.json({ ok: true, route: "/api/llm" });
}