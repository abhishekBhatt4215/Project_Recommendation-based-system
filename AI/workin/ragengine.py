# rag_engine.py  – Yesterday's working version

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np

from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RAG_MODEL = os.getenv("GEMINI_RAG_MODEL", "gemini-1.5-flash")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("[RAG] No Gemini API key — summarization disabled.")

class RAGEngine:
    def __init__(self, index_dir="rag_index"):
        os.makedirs(index_dir, exist_ok=True)
        self.index_file = os.path.join(index_dir, "vector_store.json")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.docs: List[Dict[str, Any]] = []
        self._load()

    # ------------------------ Load/Save ------------------------
    def _load(self):
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    self.docs = json.load(f)
            except:
                self.docs = []
        else:
            self.docs = []

    def _save(self):
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self.docs, f, indent=2, ensure_ascii=False)
        except:
            pass

    # ------------------------ Embedding ------------------------
    def _embed(self, text: str):
        if not text:
            text = ""
        return self.embedder.encode(text).tolist()

    def _add(self, text: str, metadata: dict):
        vec = self._embed(text)
        self.docs.append({"text": text, "metadata": metadata, "vector": vec})

    # ------------------------ Load Python Docs ------------------------
    def load_docs(self, docs):
        self.docs = []  # reset for clean index build
        if isinstance(docs, dict):
            for title, content in docs.items():
                self._add(content, {"title": title})
        elif isinstance(docs, list):
            for d in docs:
                if not isinstance(d, dict):
                    continue
                text = d.get("content", "")
                meta = {
                    "state": d.get("state", ""),
                    "title": d.get("title", "TravelDoc"),
                }
                self._add(text, meta)
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
            print("[RAG] PDF folder missing:", folder)
            return

        pdfs = list(folder.glob("*.pdf"))[:max_pdfs]

        for pdf in pdfs:
            try:
                mb = pdf.stat().st_size / (1024 * 1024)
                if mb > max_pdf_size_mb:
                    print("[RAG] Skipping large PDF:", pdf)
                    continue

                reader = PdfReader(str(pdf))
                pages = reader.pages[:max_chunks_per_pdf]
                raw = "\n".join((p.extract_text() or "") for p in pages).strip()

                if not raw:
                    print("[RAG] No text in PDF:", pdf)
                    continue

                chunks = [raw[i:i + chunk_size] for i in range(0, len(raw), chunk_size)]
                for chunk in chunks:
                    self._add(chunk, {"title": pdf.name})

                print("[RAG] Loaded PDF:", pdf.name)

            except Exception as e:
                print("[RAG] PDF error:", pdf, e)

        self._save()

    # ------------------------ SEARCH ------------------------
    def search(self, query: str, top_k=5, state: Optional[str] = None, summarize=False):
        if not self.docs:
            return "[RAG] No docs available."

        qvec = np.array(self._embed(query))
        scored = []

        for d in self.docs:
            meta = d.get("metadata", {})
            if state:
                st = (meta.get("state", "") or "").lower()
                title = (meta.get("title", "") or "").lower()
                if state.lower() not in st and state.lower() not in title:
                    continue

            dvec = np.array(d["vector"])
            score = float(np.dot(qvec, dvec) / (np.linalg.norm(qvec) * np.linalg.norm(dvec) + 1e-9))
            scored.append((score, d))

        if not scored:
            return "[RAG] No relevant documents."

        scored.sort(key=lambda x: x[0], reverse=True)
        top_docs = scored[:top_k]
        text = "\n".join(d["text"] for _, d in top_docs)

        # No summarization needed
        if not summarize or not GEMINI_API_KEY:
            return text

        # Summarize via Gemini
        try:
            model = genai.GenerativeModel(RAG_MODEL)
            prompt = f"""
Summarize the following India travel data into bullet points:

{text}
"""
            resp = model.generate_content(prompt)
            return resp.text
        except Exception as e:
            print("[RAG] Summarizer error:", e)
            return text
