from pathlib import Path

from langchain_core.documents import Document


def create_documents(files, repository: str) -> list[Document]:
    documents = []

    for file in files:
        content = file.read_text(encoding="utf-8")

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "repository": repository,
                    "file_path": str(file),
                    "file_name": file.name,
                    "extension": file.suffix,
                    "language": file.suffix.lstrip("."),
                },
            )
        )

    return documents