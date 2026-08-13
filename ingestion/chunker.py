from langchain_core.documents import Document
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter


EXT_TO_LANGUAGE = {
    ".py": Language.PYTHON,
    ".js": Language.JS,
    ".ts": Language.TS,
    ".tsx": Language.TS,
    ".jsx": Language.JS,
    ".java": Language.JAVA,
    ".cpp": Language.CPP,
    ".hpp": Language.CPP,
    ".c": Language.C,
    ".h": Language.C,
    ".go": Language.GO,
    ".rs": Language.RUST,
    ".rb": Language.RUBY,
    ".php": Language.PHP,
    ".cs": Language.CSHARP,
    ".swift": Language.SWIFT,
    ".kt": Language.KOTLIN,
}


def split_documents(documents: list[Document]) -> list[Document]:
    chunks = []

    for document in documents:
        extension = document.metadata.get("extension", "").lower()
        lang = EXT_TO_LANGUAGE.get(extension)

        if lang:
            splitter = RecursiveCharacterTextSplitter.from_language(
                language=lang,
                chunk_size=1000,
                chunk_overlap=200,
            )
        else:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""],
            )

        document_chunks = splitter.split_documents([document])

        for index, chunk in enumerate(document_chunks):
            chunk.metadata["chunk_index"] = index

        chunks.extend(document_chunks)

    return chunks