from fastapi.testclient import TestClient

import ragapp.main as main

client = TestClient(main.app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_ask_uses_llm_and_returns_sources(monkeypatch):
    monkeypatch.setattr(
        main, "search",
        lambda q: [{"text": "Argo CD syncs Git to the cluster.",
                    "source": "argocd.md", "score": 0.9}],
    )
    monkeypatch.setattr(main, "generate", lambda system,
                        user: "It syncs Git to the cluster. [argocd.md]")
    r = client.post("/ask", json={"question": "what does argo do?"})
    assert r.status_code == 200
    assert r.json()["sources"] == ["argocd.md"]
    assert "syncs" in r.json()["answer"]


def test_ask_without_relevant_hits_skips_llm(monkeypatch):
    monkeypatch.setattr(main.config, "MIN_SCORE", 0.5)
    monkeypatch.setattr(main, "search", lambda q: [
                        {"text": "x", "source": "a.md", "score": 0.1}])

    def boom(*args, **kwargs):
        raise AssertionError("LLM must not be called")

    monkeypatch.setattr(main, "generate", boom)
    r = client.post("/ask", json={"question": "unrelated"})
    assert "don't know" in r.json()["answer"]
