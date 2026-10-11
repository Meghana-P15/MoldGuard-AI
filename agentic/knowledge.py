from __future__ import annotations

from pathlib import Path
from functools import lru_cache
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from agentic.config import settings


class KnowledgeIndex:
    def __init__(self):
        self.docs: list[dict[str, Any]] = []
        self.vectorizer = None
        self.matrix = None
        self.embedding_model = None
        self.embeddings = None
        self.mode = "tfidf"
        self._load()
        self._index()

    def _load(self):
        root = Path(settings.knowledge_dir)
        if not root.exists():
            return
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".md", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            section = "General"
            buf: list[str] = []

            def flush():
                nonlocal buf
                chunk = " ".join(buf).strip()
                if len(chunk) >= 30:
                    self.docs.append(
                        {
                            "source": str(path.relative_to(root)),
                            "section": section,
                            "text": chunk,
                        }
                    )
                buf = []

            for raw in text.splitlines():
                line = raw.strip()
                if line.startswith("#"):
                    flush()
                    section = line.lstrip("#").strip() or "General"
                elif line:
                    buf.append(line)
                elif buf:
                    flush()
            flush()

    def _index(self):
        if not self.docs:
            return
        texts = [d["text"] for d in self.docs]

        if settings.rag_embedder == "sentence-transformer":
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer(
                    "sentence-transformers/all-MiniLM-L6-v2"
                )
                self.embeddings = self.embedding_model.encode(
                    texts,
                    normalize_embeddings=True,
                )
                self.mode = "sentence-transformer"
                return
            except Exception:
                pass

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
        )
        self.matrix = self.vectorizer.fit_transform(texts)
        self.mode = "tfidf"

    def search(self, query: str, k: int = 3) -> list[dict[str, Any]]:
        if not self.docs:
            return []

        if self.mode == "sentence-transformer" and self.embedding_model is not None:
            q = self.embedding_model.encode([query], normalize_embeddings=True)[0]
            scores = np.asarray(self.embeddings) @ q
        else:
            q = self.vectorizer.transform([query])
            scores = (self.matrix @ q.T).toarray().ravel()

        order = np.argsort(scores)[::-1][:k]
        out = []
        for idx in order:
            score = float(scores[idx])
            if score <= 0:
                continue
            doc = self.docs[int(idx)]
            out.append(
                {
                    "source": doc["source"],
                    "section": doc["section"],
                    "snippet": doc["text"][:700],
                    "score": round(score, 5),
                    "retrieval_mode": self.mode,
                }
            )
        return out


@lru_cache(maxsize=1)
def get_knowledge_index() -> KnowledgeIndex:
    return KnowledgeIndex()
