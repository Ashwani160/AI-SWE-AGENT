from ingestion.loader import load_files
from ingestion.file_filter import filter_files
from ingestion.documents import create_documents
from ingestion.chunker import split_documents

repo_path = "repositories/requests"

files = load_files(repo_path)
files = filter_files(files)

documents = create_documents(
    files,
    repository="requests",
)
chunks = split_documents(documents)

print(f"Files: {len(documents)}")
print(f"Chunks: {len(chunks)}")

for chunk in chunks[:3]:
    print("\n--- Chunk ---")
    print("Metadata:", chunk.metadata)
    print("Content:")
    print(chunk.page_content[:500])