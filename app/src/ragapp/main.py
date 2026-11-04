import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import config
from .llm import generate
from .prompting import SYSTEM_PROMPT, build_user_message
from .store import search

logger = logging.getLogger("ragapp")
NO_ANSWER = "I don't know based on the available documents."

app = FastAPI(title="RAG Assistant")


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str] = []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    hits = [h for h in search(req.question) if h["score"] >= config.MIN_SCORE]
    if not hits:
        return AskResponse(answer=NO_ANSWER)
    try:
        answer = generate(
            SYSTEM_PROMPT, build_user_message(req.question, hits))
    except Exception:
        logger.exception("LLM call failed")
        raise HTTPException(
            status_code=502, detail="The language model is unavailable, try again later.")
    return AskResponse(answer=answer, sources=sorted({h["source"] for h in hits}))
