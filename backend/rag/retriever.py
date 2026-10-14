from backend.rag.vector_store import collection
from backend.rag.embeddings import create_embedding


def retrieve(query: str, top_k: int = 2):

    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results["documents"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    retrieved = []

    for document, distance, metadata in zip(
        documents,
        distances,
        metadatas
    ):
        retrieved.append({
            "document": document,
            "distance": distance,
            "metadata": metadata
        })

    return retrieved