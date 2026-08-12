from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
}

ALLOWED_EXTENSIONS = {
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
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
}


def should_ignore(path: Path) -> bool:
    return any(part in IGNORED_DIRECTORIES for part in path.parts)


def filter_files(files):
    return [
        file
        for file in files
        if not should_ignore(file)
        and file.suffix.lower() in ALLOWED_EXTENSIONS
    ]