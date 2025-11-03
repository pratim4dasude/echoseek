from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from llm_rag_wrapper import llm_chat, reset_state

# CORS
app = FastAPI(title="EchoSeek RAG API")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


class LLMQueryRequest(BaseModel):
    user_input: str = Field(..., description="User's search query")


class ProductLink(BaseModel):
    id: str
    title: str
    url: str
    image: Optional[str] = None
    price: Optional[str] = None
    rating: Optional[float] = None


class LLMQueryResponse(BaseModel):
    text: str
    links: List[ProductLink]
    meta: Dict[str, Any] = {}


# ROUTES
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is working"}


@app.post("/api/reset")
def reset_endpoint():
    reset_state()
    return {"status": "ok", "message": "state reset"}


@app.post("/api/llm_query", response_model=LLMQueryResponse)
def handle_llm_query(data: LLMQueryRequest, x_reset: Optional[str] = Header(default=None)):
    if x_reset == "1":
        reset_state()

    user_input = data.user_input.strip()
    if not user_input:
        raise HTTPException(status_code=400, detail="'user_input' must be a non-empty string.")

    try:
        payload = llm_chat(user_input)
    except Exception as e:
        print(f"[ERROR] LLM processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"LLM processing failed: {e}")

    return payload


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
