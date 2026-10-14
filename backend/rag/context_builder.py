from backend.rag.retriever import retrieve


def build_context(query: str, top_k: int = 2):

    results = retrieve(query, top_k)

    context_parts = []

    for result in results:

        source = result["metadata"]["source"]
        chunk = result["metadata"]["chunk_index"]
        document = result["document"]

        context_parts.append(
            f"[Source: {source}, Chunk: {chunk}]\n"
            f"{document}"
        )

    return "\n\n".join(context_parts)