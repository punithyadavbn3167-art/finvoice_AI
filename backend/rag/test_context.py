from backend.rag.context_builder import build_context


query = "How much revenue did the company make?"

context = build_context(query)

print("\n===== RAG CONTEXT =====")
print(context)