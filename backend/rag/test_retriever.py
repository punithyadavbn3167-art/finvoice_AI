from backend.rag.retriever import retrieve


query = "How much revenue did the company make?"

results = retrieve(query)

print("\nRetrieved chunks:")

for i, result in enumerate(results):

    print(f"\n--- Result {i + 1} ---")
    print("Distance:", result["distance"])
    print("Source:", result["metadata"]["source"])
    print("Chunk:", result["metadata"]["chunk_index"])
    print(result["document"])