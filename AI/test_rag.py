# test_rag.py

from rag_engine import RAGEngine
from rag_documents import india_travel_docs


def main():
    rag = RAGEngine()

    if not rag.docs:
        print("[RAG] Empty index, loading base docs + PDFs...")
        rag.load_docs(india_travel_docs)
        rag.load_pdfs_from_folder(
            "rag_pdfs",
            max_pdfs=3,
            max_chunks_per_pdf=8,
        )
    else:
        print(f"[RAG] Loaded {len(rag.docs)} docs from existing index.")

    print("\nType a travel question about India (or 'q' to quit).\n")
    while True:
        try:
            query = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not query or query.lower() in {"q", "quit", "exit"}:
            break

        answer = rag.search(query, summarize=True)
        print("\n--- RAG RESULT (context summary) ---\n")
        print(answer)
        print("\n------------------------------------\n")


if __name__ == "__main__":
    main()
