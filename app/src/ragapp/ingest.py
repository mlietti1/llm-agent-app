import sys
from pathlib import Path

from .chunking import chunk_text
from .store import add_chunks, reset_collection


def main():
    docs_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "../docs")
    chunks = []
    for path in sorted(docs_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for part in chunk_text(text):
            chunks.append({"text": part, "source": path.name})
    if not chunks:
        sys.exit(f"No .md files found in {docs_dir}")
    reset_collection()
    add_chunks(chunks)
    print(f"Ingested {len(chunks)} chunks from {docs_dir}")


if __name__ == "__main__":
    main()
