from backend.rag.document_loader import load_pdf
from backend.rag.chunker import chunk_text


text = load_pdf("test_financial_report.pdf")

chunks = chunk_text(text, chunk_size=100)

for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i + 1} ---")
    print(chunk)