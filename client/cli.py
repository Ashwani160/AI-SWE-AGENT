import requests

import os
API_BASE_URL = os.getenv(
    "REPORAG_API_URL",
    "https://ashwani.viewdns.net",
)

def index_repository(
    repository_url: str,
    repository_name: str,
    chunking_strategy: str,
    reindex: bool,
):
    payload = {
        "repository_url": repository_url,
        "repository_name": repository_name,
        "chunking_strategy": chunking_strategy,
        "reindex": reindex,
    }

    response = requests.post(
        f"{API_BASE_URL}/repositories/index",
        json=payload,
        timeout=300,
    )

    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text

        raise RuntimeError(
            f"Repository indexing failed: {detail}"
        )

    return response.json()


def ask_question(
    question: str,
    repository_name: str,
    chunking_strategy: str,
):
    payload = {
        "question": question,
        "repository_name": repository_name,
        "chunking_strategy": chunking_strategy,
    }

    response = requests.post(
        f"{API_BASE_URL}/chat",
        json=payload,
        timeout=300,
    )

    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text

        raise RuntimeError(
            f"Chat request failed: {detail}"
        )

    return response.json()


def format_source(source: object) -> str:
    """Format an API source object for terminal output."""
    if not isinstance(source, dict):
        return str(source)

    file_path = source.get("file", "Unknown source")
    start_line = source.get("start_line")
    end_line = source.get("end_line")
    score = source.get("score")

    location = str(file_path)
    if start_line is not None and end_line is not None:
        location = f"{location}#L{start_line}-L{end_line}"

    if isinstance(score, (int, float)):
        return f"{location} (score: {score:.3f})"

    return location


def run():
    print("=" * 50)
    print("RepoRAG - AI Software Engineering Assistant")
    print("API Client CLI")
    print("=" * 50)

    repository_url = input("\nRepository URL: ").strip()

    if not repository_url:
        print("Repository URL cannot be empty.")
        return

    repository_name = (
        repository_url.rstrip("/").split("/")[-1]
    )
    repository_name = repository_name.removesuffix(".git")

    print(f"\nRepository: {repository_name}")

    print("\nChoose chunking strategy:")
    print("1. Language-aware")
    print("2. AST")

    strategy_choice = input("Choice (1/2): ").strip()

    if strategy_choice == "2":
        chunking_strategy = "ast"
        print("Using AST chunking.")
    else:
        chunking_strategy = "language"
        print("Using language-aware chunking.")

    reindex_choice = input(
        "\nRe-index repository? (y/n): "
    ).strip().lower()

    reindex = reindex_choice == "y"

    print("\nConnecting to RepoRAG API...")

    try:
        result = index_repository(
            repository_url=repository_url,
            repository_name=repository_name,
            chunking_strategy=chunking_strategy,
            reindex=reindex,
        )

        print("\n" + "=" * 50)
        print("REPOSITORY READY")
        print("=" * 50)

        print(f"Repository: {result['repository']}")
        print(
            f"Strategy:   {result['chunking_strategy']}"
        )
        print(f"Indexed:    {result['indexed']}")

        if "files" in result:
            print(f"Files:      {result['files']}")

        if "chunks" in result:
            print(f"Chunks:     {result['chunks']}")

        if "collection" in result:
            print(f"Collection: {result['collection']}")

    except requests.ConnectionError:
        print(
            "\nCould not connect to the RepoRAG API."
        )
        print(
            "Make sure FastAPI is running:"
        )
        print(
            "uvicorn backend.main:app --reload"
        )
        return

    except requests.Timeout:
        print("\nThe API request timed out.")
        return

    except RuntimeError as error:
        print(f"\nError: {error}")
        return

    print("\nYou can now ask questions about the repository.")
    print("Type 'exit' to quit.")

    while True:
        question = input("\n> ").strip()

        if question.lower() == "exit":
            break

        if not question:
            continue

        try:
            result = ask_question(
                question=question,
                repository_name=repository_name,
                chunking_strategy=chunking_strategy,
            )

            print("\n" + result["answer"])

            print("\nSources:")
            displayed_sources: set[str] = set()
            for source in result.get("sources", []):
                formatted_source = format_source(source)
                if formatted_source in displayed_sources:
                    continue

                displayed_sources.add(formatted_source)
                print(f"- {formatted_source}")

        except requests.ConnectionError:
            print(
                "\nLost connection to the RepoRAG API."
            )
            break

        except requests.Timeout:
            print("\nThe API request timed out.")

        except RuntimeError as error:
            print(f"\nError: {error}")


if __name__ == "__main__":
    run()
