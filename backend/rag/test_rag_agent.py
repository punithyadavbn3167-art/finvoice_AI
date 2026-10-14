from backend.rag.rag_agent import run_rag_agent


question = "What was the company's revenue?"

answer = run_rag_agent(question)

print("\n===== RAG ANSWER =====")
print(answer)