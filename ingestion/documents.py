from pathlib import Path

from langchain_core.documents import Document


def create_documents(
    files,
    repository: str,
    repo_path: str,
) -> list[Document]:
    documents = []

    repo_root = Path(repo_path).resolve()

    for file in files:
        content = file.read_text(encoding="utf-8")

        relative_path = file.resolve().relative_to(repo_root)

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "repository": repository,
                    "file_path": str(relative_path).replace("\\", "/"),
                    "file_name": file.name,
                    "extension": file.suffix,
                    "language": file.suffix.lstrip("."),
                },
            )
        )

    return documents