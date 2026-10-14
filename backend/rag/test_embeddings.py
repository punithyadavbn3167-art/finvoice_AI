from backend.rag.document_loader import load_pdf
from backend.rag.chunker import chunk_text
from backend.rag.embeddings import create_embeddings


text = load_pdf("test_financial_report.pdf")

chunks = chunk_text(text, chunk_size=100)

embeddings = create_embeddings(chunks)

print("Number of chunks:", len(chunks))
print("Number of embeddings:", len(embeddings))

for i, embedding in enumerate(embeddings):
    print(f"Chunk {i + 1}: {len(embedding)} dimensions")