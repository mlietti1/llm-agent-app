import logging

from openai import APIConnectionError, APIStatusError, OpenAI

from . import config

logger = logging.getLogger("ragapp")
RETRYABLE = {429, 500, 502, 503, 504}
_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not config.LLM_API_KEY:
            raise RuntimeError("LLM_API_KEY is not set")
        _client = OpenAI(
            base_url=config.LLM_BASE_URL,
            api_key=config.LLM_API_KEY,
            timeout=30,
            max_retries=config.LLM_MAX_RETRIES,
        )
    return _client


def _call(model: str, system: str, user: str) -> str:
    resp = get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0,
    )
    return resp.choices[0].message.content


def generate(system: str, user: str) -> str:
    try:
        return _call(config.LLM_MODEL, system, user)
    except (APIStatusError, APIConnectionError) as exc:
        # None for connection errors
        status = getattr(exc, "status_code", None)
        retryable = status is None or status in RETRYABLE
        if not (config.LLM_FALLBACK_MODEL and retryable):
            raise
        logger.warning(
            "Model %s failed (%s); falling back to %s",
            config.LLM_MODEL, status, config.LLM_FALLBACK_MODEL,
        )
        return _call(config.LLM_FALLBACK_MODEL, system, user)
