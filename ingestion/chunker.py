from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


CODE_SEPARATORS = [
    "\nclass ",
    "\nasync def ",
    "\ndef ",
    "\n\n",
    "\n",
    " ",
    "",
]


DEFAULT_SEPARATORS = [
    "\n\n",
    "\n",
    " ",
    "",
]


CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".cs",
    ".swift",
    ".kt",
}


def split_documents(documents: list[Document]) -> list[Document]:
    chunks = []

    for document in documents:
        extension = document.metadata.get("extension", "").lower()

        separators = (
            CODE_SEPARATORS
            if extension in CODE_EXTENSIONS
            else DEFAULT_SEPARATORS
        )

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=separators,
        )

        chunks.extend(splitter.split_documents([document]))

    return chunks