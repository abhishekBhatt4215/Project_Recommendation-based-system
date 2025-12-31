# rag_engine.py — FAISS Vector RAG Core

import os
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from dotenv import load_dotenv

from llm.groq_llm import call_groq

# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()

RAG_SUMMARY_MODEL = os.getenv(
    "RAG_SUMMARY_MODEL",
    "llama-3.1-8b-instant"
)

# -------------------------------------------------
# RAG ENGINE
# -------------------------------------------------
class RAGEngine:
    def __init__(self, index_dir: str = "rag_index"):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)

        self.index_path = os.path.join(index_dir, "faiss.index")
        self.meta_path = os.path.join(index_dir, "metadata.pkl")

        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.dim = self.embedder.get_sentence_embedding_dimension()

        self.index = faiss.IndexFlatIP(self.dim)
        self.metadata: List[Dict[str, Any]] = []

        self._load()

    # ------------------------ Persistence ------------------------
    def _load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.meta_path, "rb") as f:
                    self.metadata = pickle.load(f)
            except Exception:
                self.index = faiss.IndexFlatIP(self.dim)
                self.metadata = []

    def _save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

    # ------------------------ Embedding ------------------------
    def _embed(self, texts: List[str]) -> np.ndarray:
        vecs = self.embedder.encode(texts, normalize_embeddings=True)
        return np.array(vecs).astype("float32")

    # ------------------------ Add Docs ------------------------
    def _add(self, text: str, metadata: dict):
        if not text.strip():
            return

        vec = self._embed([text])
        self.index.add(vec)
        self.metadata.append({
            "text": text.strip(),
            "metadata": metadata
        })

    # ------------------------ Load Docs ------------------------
    def load_docs(self, docs):
        """
        Supports:
        - list[str]
        - list[dict]
        - dict[str, str]
        """
        self.index.reset()
        self.metadata = []

        if isinstance(docs, list) and all(isinstance(d, str) for d in docs):
            for text in docs:
                self._add(text, {"title": "TravelDoc"})

        elif isinstance(docs, list):
            for d in docs:
                if not isinstance(d, dict):
                    continue
                self._add(
                    d.get("content", ""),
                    {
                        "state": d.get("state", ""),
                        "title": d.get("title", "TravelDoc"),
                    }
                )

        elif isinstance(docs, dict):
            for title, content in docs.items():
                self._add(content, {"title": title})

        self._save()

    # ------------------------ Load PDFs ------------------------
    def load_pdfs_from_folder(
        self,
        folder="rag_pdfs",
        max_pdfs=3,
        max_chunks_per_pdf=8,
        chunk_size=500,
        max_pdf_size_mb=15,
    ):
        folder = Path(folder)
        if not folder.exists():
            return

        pdfs = list(folder.glob("*.pdf"))[:max_pdfs]

        for pdf in pdfs:
            try:
                if pdf.stat().st_size / (1024 * 1024) > max_pdf_size_mb:
                    continue

                reader = PdfReader(str(pdf))
                pages = reader.pages[:max_chunks_per_pdf]
                raw = "\n".join((p.extract_text() or "") for p in pages).strip()

                if not raw:
                    continue

                chunks = [
                    raw[i:i + chunk_size]
                    for i in range(0, len(raw), chunk_size)
                ]

                for chunk in chunks:
                    self._add(chunk, {"title": pdf.name})

            except Exception:
                continue

        self._save()

    # ------------------------ SEARCH ------------------------
    def search(
        self,
        query: str,
        top_k: int = 5,
        state: Optional[str] = None,
        summarize: bool = False
    ):
        if self.index.ntotal == 0:
            return "[RAG] No documents available."

        qvec = self._embed([query])
        scores, indices = self.index.search(qvec, top_k)

        results = []
        for idx in indices[0]:
            if idx < 0 or idx >= len(self.metadata):
                continue

            doc = self.metadata[idx]
            meta = doc.get("metadata", {})

            if state:
                combined = (
                    (meta.get("state", "") or "") +
                    (meta.get("title", "") or "")
                ).lower()
                if state.lower() not in combined:
                    continue

            results.append(doc["text"])

        if not results:
            return "[RAG] No relevant documents."

        context = "\n".join(results)

        if not summarize:
            return context

        # -------- Groq summarization --------
        try:
            prompt = f"""
Summarize the following India travel information into concise bullet points.
Focus on attractions, tips, logistics, safety, and best times.

{context}
"""
            return call_groq(
                prompt,
                model=RAG_SUMMARY_MODEL
            )

        except Exception:
            return context

