from __future__ import annotations

from pathlib import Path
from typing import Any
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from backend.app.config import settings


class KnowledgeService:
    _instance = None

    def __init__(self):
        self.docs: list[dict[str, Any]] = []
        self.vectorizer = None
        self.matrix = None
        self.embedding_model = None
        self.embeddings = None
        self.mode = "tfidf"
        self._load_documents()
        self._build_index()

    @classmethod
    def instance(cls) -> "KnowledgeService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_documents(self):
        root = Path(settings.knowledge_dir)
        if not root.exists():
            return

        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".md", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            heading = ""
            chunks = []
            current = []
            for line in text.splitlines():
                if line.startswith("#"):
                    if current:
                        chunks.append((heading, "\n".join(current).strip()))
                        current = []
                    heading = line.lstrip("#").strip()
                elif line.strip():
                    current.append(line.strip())
                elif current:
                    chunks.append((heading, "\n".join(current).strip()))
                    current = []
            if current:
                chunks.append((heading, "\n".join(current).strip()))

            for section, chunk in chunks:
                if len(chunk) < 30:
                    continue
                self.docs.append({
                    "source": str(path.relative_to(root)),
                    "section": section or "General",
                    "text": chunk,
                })

    def _build_index(self):
        if not self.docs:
            return

        texts = [d["text"] for d in self.docs]

        wants_transformer = settings.rag_embedder in {"auto", "sentence-transformer"}
        if wants_transformer:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer(settings.rag_model_name)
                self.embeddings = self.embedding_model.encode(
                    texts,
                    normalize_embeddings=True,
                )
                self.mode = "sentence-transformer"
                return
            except Exception:
                if settings.rag_embedder == "sentence-transformer":
                    raise

        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(texts)
        self.mode = "tfidf"

    def retrieve(self, query: str, k: int = 3) -> list[dict[str, Any]]:
        if not self.docs:
            return []

        if self.mode == "sentence-transformer" and self.embedding_model is not None:
            q = self.embedding_model.encode([query], normalize_embeddings=True)[0]
            scores = np.asarray(self.embeddings) @ q
        else:
            q = self.vectorizer.transform([query])
            scores = (self.matrix @ q.T).toarray().ravel()

        order = np.argsort(scores)[::-1][:k]
        results = []
        for idx in order:
            score = float(scores[idx])
            if score <= 0:
                continue
            doc = self.docs[int(idx)]
            results.append({
                "source": doc["source"],
                "section": doc["section"],
                "snippet": doc["text"][:700],
                "score": round(score, 5),
                "retrieval_mode": self.mode,
            })
        return results
