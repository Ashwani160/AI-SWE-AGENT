from ingestion.loader import load_files
from ingestion.file_filter import filter_files
from ingestion.documents import create_documents
from ingestion.chunker_ast import split_documents

from rag.embeddings import embeddings
from rag.vector_store import create_collection, add_documents


repo_path = "repositories/requests"

print("1. Loading repository files...")
files = load_files(repo_path)
files = filter_files(files)

print("2. Converting files to documents...")
documents = create_documents(
    files,
    repository="requests",
    repo_path=repo_path,
)

print("3. Splitting documents using AST chunker (chunker2)...")
chunks = split_documents(documents)

print(f"--> Total Files: {len(documents)}")
print(f"--> Total AST Chunks: {len(chunks)}")

print("4. Calculating vector dimensions...")
vector_size = len(embeddings.embed_query("test"))

print("5. Initializing vector collection in Qdrant...")
create_collection(
    vector_size,
    collection_name="code_chunks_ast",
)

print("6. Embedding and pushing AST chunks to Qdrant...")
add_documents(
    chunks,
    embeddings,
    collection_name="code_chunks_ast",
)

print(f"\n✅ Successfully inserted {len(chunks)} AST chunks into Qdrant!")

# Inspection preview to verify AST metadata (node_type, start_line, end_line)
print("\n===== SAMPLE RETRIEVED AST CHUNKS =====")
for chunk in chunks[:3]:
    print("\nMetadata:", chunk.metadata)
    print("Content Preview:\n", chunk.page_content[:300])
    print("-" * 50)