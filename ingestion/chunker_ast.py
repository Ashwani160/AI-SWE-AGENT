import logging

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tree_sitter_language_pack import get_parser

logger = logging.getLogger(__name__)

EXT_TO_TREESITTER = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".java": "java",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
}

TARGET_NODE_TYPES = {
    "python": {"function_definition", "class_definition"},
    "javascript": {"function_declaration", "class_declaration", "method_definition", "export_statement"},
    "typescript": {"function_declaration", "class_declaration", "method_definition", "export_statement", "interface_declaration"},
    "tsx": {"function_declaration", "class_declaration", "method_declaration", "export_statement", "interface_declaration"},
    "java": {"class_declaration", "method_declaration", "interface_declaration"},
    "cpp": {"function_definition", "class_specifier", "struct_specifier"},
    "c": {"function_definition", "struct_specifier"},
    "go": {"function_declaration", "method_declaration", "type_declaration"},
    "rust": {"function_item", "struct_item", "enum_item", "impl_item", "trait_item"},
    "ruby": {"method", "class", "module"},
    "php": {"function_definition", "class_declaration", "method_declaration"},
    "csharp": {"class_declaration", "method_declaration", "interface_declaration"},
}


def _add_line_metadata_to_chunks(full_text: str, chunks: list[Document]) -> list[Document]:
    """Calculates start_line and end_line for fallback chunks."""
    lines = full_text.splitlines()
    
    for chunk in chunks:
        chunk_lines = chunk.page_content.strip().splitlines()
        if not chunk_lines:
            continue
            
        first_line = chunk_lines[0]
        start_line = 1
        
        for idx, line in enumerate(lines):
            if first_line in line:
                start_line = idx + 1
                break
                
        end_line = start_line + len(chunk_lines) - 1
        chunk.metadata["start_line"] = start_line
        chunk.metadata["end_line"] = end_line
        chunk.metadata["node_type"] = "raw_chunk"
        
    return chunks


def chunk_by_ast(document: Document, ts_language: str) -> list[Document]:
    """Parses code into AST nodes using tree-sitter."""
    try:
        parser = get_parser(ts_language)
        code_bytes = document.page_content.encode("utf-8")
        tree = parser.parse(code_bytes)
        root_node = tree.root_node

        target_types = TARGET_NODE_TYPES.get(ts_language, set())
        extracted_chunks: list[Document] = []

        def extract(node, node_type: str):
            chunk_code = code_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace").strip()
            if chunk_code:
                chunk_metadata = document.metadata.copy()
                chunk_metadata.update({
                    "node_type": node_type,
                    "start_line": node.start_point[0] + 1,
                    "end_line": node.end_point[0] + 1,
                })
                extracted_chunks.append(
                    Document(page_content=chunk_code, metadata=chunk_metadata)
                )

        def traverse(node):
            if node.type in target_types:
                extract(node, node.type)
            elif node.type == "decorated_definition":
                # tree-sitter-python wraps decorators (@app.route, @property, ...)
                # and the function/class they annotate in one "decorated_definition"
                # node. Extracting just the inner definition (the old behavior)
                # silently drops the decorator line, which is often the most
                # semantically useful part (e.g. the route path or fixture name).
                # Extract the whole thing, tagged with the inner node's real type.
                inner = next(
                    (c for c in node.children if c.type in ("function_definition", "class_definition")),
                    None,
                )
                extract(node, inner.type if inner else node.type)
            else:
                for child in node.children:
                    traverse(child)

        traverse(root_node)

        if extracted_chunks:
            return extracted_chunks

    except Exception:
        logger.warning(
            "AST chunking failed for %s (language=%s); falling back to text splitting",
            document.metadata.get("file_path", "<unknown>"),
            ts_language,
            exc_info=True,
        )

    # Fallback if AST extraction yields no nodes or fails
    fallback_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    raw_chunks = fallback_splitter.split_documents([document])
    return _add_line_metadata_to_chunks(document.page_content, raw_chunks)


def split_documents(documents: list[Document]) -> list[Document]:
    chunks = []
    fallback_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""],
    )

    for document in documents:
        extension = document.metadata.get("extension", "").lower()
        ts_language = EXT_TO_TREESITTER.get(extension)

        if ts_language:
            doc_chunks = chunk_by_ast(document, ts_language)
        else:
            raw_chunks = fallback_splitter.split_documents([document])
            doc_chunks = _add_line_metadata_to_chunks(document.page_content, raw_chunks)

        for index, chunk in enumerate(doc_chunks):
            chunk.metadata["chunk_index"] = index

        chunks.extend(doc_chunks)

    return chunks