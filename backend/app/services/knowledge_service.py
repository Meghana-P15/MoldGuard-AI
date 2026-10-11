from __future__ import annotations

from pathlib import Path
from typing import List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.app.config import settings


class KnowledgeService:
    _docs = None
    _backend = None
    _semantic_model = None
    _faiss_index = None
    _tfidf_vectorizer = None
    _tfidf_matrix = None

    @classmethod
    def _load_docs(cls):
        if cls._docs is not None:
            return
        root = Path(settings.knowledge_dir)
        root.mkdir(parents=True, exist_ok=True)
        docs = []
        for path in sorted(list(root.glob("*.md")) + list(root.glob("*.txt"))):
            text = path.read_text(errors="ignore").strip()
            if not text:
                continue
            # Paragraph chunks keep retrieved evidence concise and source-aware.
            for paragraph in [p.strip() for p in text.split("\n\n") if p.strip()]:
                if paragraph.startswith("#") and len(paragraph.split()) < 8:
                    continue
                docs.append({"source": path.name, "text": paragraph})
        cls._docs = docs

    @classmethod
    def _load(cls):
        cls._load_docs()
        if cls._backend is not None:
            return
        if not cls._docs:
            cls._backend = "empty"
            return

        requested = settings.rag_backend.lower().strip()
        if requested in {"auto", "semantic", "faiss", "sentence-transformers"}:
            try:
                import faiss  # type: ignore
                from sentence_transformers import SentenceTransformer  # type: ignore

                cls._semantic_model = SentenceTransformer(settings.rag_embedding_model)
                embeddings = cls._semantic_model.encode(
                    [d["text"] for d in cls._docs],
                    normalize_embeddings=True,
                    show_progress_bar=False,
                )
                embeddings = np.asarray(embeddings, dtype="float32")
                cls._faiss_index = faiss.IndexFlatIP(embeddings.shape[1])
                cls._faiss_index.add(embeddings)
                cls._backend = "sentence-transformers+faiss"
                return
            except Exception:
                if requested not in {"auto"}:
                    # Explicit semantic mode still degrades safely so the API can run
                    # offline; /api/meta reports the active backend.
                    pass

        cls._tfidf_vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        cls._tfidf_matrix = cls._tfidf_vectorizer.fit_transform(
            [d["text"] for d in cls._docs]
        )
        cls._backend = "tfidf-fallback"

    @classmethod
    def backend_name(cls) -> str:
        cls._load()
        return str(cls._backend)

    @classmethod
    def retrieve(cls, query: str, top_k: int = 3) -> List[dict]:
        cls._load()
        if not cls._docs:
            return []

        if cls._backend == "sentence-transformers+faiss":
            vector = cls._semantic_model.encode(
                [query], normalize_embeddings=True, show_progress_bar=False
            )
            vector = np.asarray(vector, dtype="float32")
            scores, indices = cls._faiss_index.search(vector, min(top_k, len(cls._docs)))
            pairs = [(int(i), float(s)) for i, s in zip(indices[0], scores[0]) if i >= 0]
        else:
            q = cls._tfidf_vectorizer.transform([query])
            scores = cosine_similarity(q, cls._tfidf_matrix)[0]
            order = scores.argsort()[::-1][:top_k]
            pairs = [(int(i), float(scores[int(i)])) for i in order]

        return [
            {
                "source": cls._docs[idx]["source"],
                "excerpt": cls._docs[idx]["text"][:700],
                "score": round(score, 4),
                "retrieval_backend": cls._backend,
            }
            for idx, score in pairs
        ]
