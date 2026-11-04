from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from . import config

_embedder = TextEmbedding(config.EMBED_MODEL, cache_dir=config.EMBED_CACHE_DIR)
_client = None


def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = TextEmbedding(config.EMBED_MODEL)
    return _embedder


def get_client():
    global _client
    if _client is None:
        _client = QdrantClient(url=config.QDRANT_URL)
    return _client


def reset_collection():
    client = get_client()
    if client.collection_exists(config.COLLECTION):
        client.delete_collection(config.COLLECTION)
    client.create_collection(
        collection_name=config.COLLECTION,
        vectors_config=VectorParams(
            size=config.VECTOR_SIZE, distance=Distance.COSINE),
    )


def add_chunks(chunks: list[dict]):
    """chunks: [{"text": ..., "source": ...}]"""
    vectors = list(get_embedder().embed([c["text"] for c in chunks]))
    points = [
        PointStruct(id=i, vector=v.tolist(), payload=c)
        for i, (v, c) in enumerate(zip(vectors, chunks))
    ]
    get_client().upsert(collection_name=config.COLLECTION, points=points)


def search(question: str, k: int = config.TOP_K) -> list[dict]:
    vector = next(iter(get_embedder().query_embed(question))).tolist()
    res = get_client().query_points(
        collection_name=config.COLLECTION, query=vector, limit=k, with_payload=True
    )
    return [
        {"text": p.payload["text"],
            "source": p.payload["source"], "score": p.score}
        for p in res.points
    ]
