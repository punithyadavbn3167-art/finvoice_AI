from backend.rag.document_loader import load_pdf
from backend.rag.chunker import chunk_text
from backend.rag.embeddings import create_embeddings
from backend.rag.vector_store import store_chunks


text = load_pdf("test_financial_report.pdf")

chunks = chunk_text(
    text,
    chunk_size=100
)

embeddings = create_embeddings(chunks)

result = store_chunks(
    chunks,
    embeddings
)

print(result)