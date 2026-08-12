from rag.embeddings import embeddings

text = "Where is the database connection created?"

vector = embeddings.embed_query(text)

print("Embedding dimensions:", len(vector))
print("First 5 values:", vector[:5])