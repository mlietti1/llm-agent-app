import httpx
import pytest
from openai import APIStatusError

import ragapp.llm as llm
from ragapp import config


def _status_error(code: int) -> APIStatusError:
    req = httpx.Request("POST", "http://example.test")
    return APIStatusError("boom", response=httpx.Response(code, request=req), body=None)


def test_falls_back_on_503(monkeypatch):
    monkeypatch.setattr(config, "LLM_FALLBACK_MODEL", "backup")
    calls = []

    def fake_call(model, system, user):
        calls.append(model)
        if model == config.LLM_MODEL:
            raise _status_error(503)
        return "ok"

    monkeypatch.setattr(llm, "_call", fake_call)
    assert llm.generate("s", "u") == "ok"
    assert calls == [config.LLM_MODEL, "backup"]


def test_no_fallback_on_401(monkeypatch):
    monkeypatch.setattr(config, "LLM_FALLBACK_MODEL", "backup")

    def raise_401(model, system, user):
        raise _status_error(401)

    monkeypatch.setattr(llm, "_call", raise_401)
    with pytest.raises(APIStatusError):
        llm.generate("s", "u")
