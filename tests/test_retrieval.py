from rag.embeddings import embeddings
from rag.vector_store import search_documents


query = "How do I send a request with authentication?"

results = search_documents(
    query,
    embeddings,
    limit=5,
)

for result in results:
    print("\n--- Result ---")
    print("Score:", result.score)
    print("File:", result.payload["file_path"])
    print(result.payload["text"][:500])