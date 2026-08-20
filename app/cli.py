from pathlib import Path

from ingestion.cloner import clone_repository
from app.services.indexing import index_repository
from app.services.chat import answer_question


def run():
    print("=" * 50)
    print("RepoRAG - AI Software Engineering Assistant")
    print("=" * 50)

    repository_url = input("\nRepository URL: ").strip()

    repository_name = repository_url.rstrip("/").split("/")[-1]
    repository_name = repository_name.removesuffix(".git")

    destination = Path("repositories") / repository_name

    print(f"\nPreparing repository: {repository_name}...")

    clone_repository(
        repository_url,
        str(destination),
    )

    print(f"Repository ready at: {destination}")

    print("\nChoose chunking strategy:")
    print("1. Language-aware")
    print("2. AST")

    strategy_choice = input("Choice (1/2): ").strip()

    if strategy_choice == "2":
        collection_name = "code_chunks_ast"
        print("Using AST chunking.")
    else:
        collection_name = "code_chunks_lang"
        print("Using language-aware chunking.")

    reindex = input("\nRe-index repository? (y/n): ").strip().lower()

    if reindex == "y":
        print("\nChoose chunking strategy:")
        print("1. Language-aware")
        print("2. AST")
            
        print("\nStarting indexing...")

        result = index_repository(
            repo_path=str(destination),
            repository=repository_name,
            collection_name=collection_name,
        )
        print("\n" + "=" * 50)
        print("INDEXING COMPLETE")
        print("=" * 50)
        print(f"Files:      {result['files']}")
        print(f"Chunks:     {result['chunks']}")

    else:
        print("\nUsing existing index.")

    print("\nYou can now ask questions about the repository.")
    print("Type 'exit' to quit.")

    while True:
        question = input("\n> ").strip()

        if question.lower() == "exit":
            break

        answer, sources = answer_question(
            question=question,
            repository=repository_name,
            collection_name=collection_name,
        )

        print("\n" + answer)

        print("\nSources:")
        for source in dict.fromkeys(sources):
            print(f"- {source}")