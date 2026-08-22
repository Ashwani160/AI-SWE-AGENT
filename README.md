# RepoRAG

> **AI-powered codebase question answering for GitHub repositories**

RepoRAG is a console-based Retrieval-Augmented Generation (RAG) system that allows developers to ask natural-language questions about a GitHub repository and receive answers grounded in the repository's source code.

The system clones a repository, filters irrelevant files, converts source files into LangChain documents, applies code-aware chunking, generates embeddings using OpenAI, stores the resulting vectors in Qdrant, retrieves relevant code using semantic search, and uses an LLM to generate grounded answers with source references.

The project is being developed incrementally toward an AI software engineering assistant, with the current milestone focused on building a reliable repository-level RAG foundation.

---

## Features

* **GitHub repository ingestion**

  * Clone repositories directly from GitHub URLs.
  * Reuse an already-cloned repository without cloning it again.
  * Support repository re-indexing when required.

* **Code-aware document processing**

  * Filter irrelevant files such as virtual environments, build artifacts, caches, and binary files.
  * Convert repository files into LangChain `Document` objects.
  * Preserve repository and file metadata throughout the pipeline.

* **Multiple chunking strategies**

  * Language-aware chunking using LangChain's `RecursiveCharacterTextSplitter`.
  * AST-based chunking using Tree-sitter.
  * AST chunks preserve structural information such as classes, functions, methods, and interfaces where supported.

* **Semantic code retrieval**

  * Generate embeddings using OpenAI embedding models.
  * Store vectors in Qdrant.
  * Retrieve the most relevant code chunks using cosine similarity.
  * Support repository metadata filtering.
  * Support configurable similarity thresholds.

* **Grounded LLM answers**

  * Answers are generated using retrieved repository context.
  * The model is instructed not to invent unsupported information.
  * Retrieved source files are displayed alongside answers.

* **AST source citations**

  * AST-based chunks retain source line information.
  * Results can be displayed as file and line ranges, for example:
    `src/requests/sessions.py#L908-L920`

* **Retrieval evaluation**

  * Includes a question/expected-source evaluation dataset.
  * Measures whether the expected source file appears in the retrieved top-k results.
  * Separate evaluation exists for language-aware and AST-based retrieval.

---

## Architecture

### Current CLI architecture

```text
                    GitHub Repository
                           │
                           ▼
                    Repository Cloner
                           │
                           ▼
                    File Loader
                           │
                           ▼
                     File Filter
                           │
                           ▼
                  LangChain Documents
                           │
                 ┌─────────┴─────────┐
                 │                   │
                 ▼                   ▼
        Language-Aware            AST-Based
          Chunking                Chunking
                 │                   │
                 ▼                   ▼
          code_chunks_lang     code_chunks_ast
                 │                   │
                 └─────────┬─────────┘
                           ▼
                  OpenAI Embeddings
                           │
                           ▼
                       Qdrant
                           │
                    Semantic Search
                           │
                           ▼
                    Retrieved Code
                           │
                           ▼
                       LLM
                           │
                           ▼
                    Console Answer
                           │
                           ▼
                       Sources
```

---

## RAG Pipeline

RepoRAG follows a standard retrieval-augmented generation pipeline adapted specifically for source code.

### 1. Repository ingestion

A GitHub repository URL is provided through the CLI.

```text
GitHub URL
    ↓
Clone repository
    ↓
repositories/<repository>
```

If the repository has already been cloned, RepoRAG reuses the existing working copy.

### 2. File processing

Repository files are loaded and filtered before entering the RAG pipeline.

The resulting files are converted into LangChain `Document` objects with metadata including:

```text
repository
file_path
file_name
extension
language
```

### 3. Chunking

RepoRAG supports two chunking approaches.

#### Language-aware chunking

The implementation uses LangChain's language-specific recursive splitter where a supported programming language is detected.

Example:

```text
Python
JavaScript
TypeScript
C/C++
Go
Rust
Ruby
PHP
C#
Swift
Kotlin
```

Chunks currently use:

```text
chunk_size: 1000
chunk_overlap: 200
```

Each chunk also receives a `chunk_index` for identification.

#### AST-based chunking

The second strategy uses Tree-sitter to parse source code and extract structural nodes such as:

```text
class
function
method
interface
struct
module
```

AST chunks retain additional metadata:

```text
node_type
start_line
end_line
```

This enables more precise source references.

---

## Vector Storage

Qdrant is used as the vector database.

The project maintains separate collections for the two chunking strategies:

```text
code_chunks_lang
code_chunks_ast
```

Each stored point contains the embedded code along with its metadata.

Example payload:

```json
{
  "text": "...source code...",
  "repository": "requests",
  "file_path": "src/requests/sessions.py",
  "file_name": "sessions.py",
  "extension": ".py",
  "language": "py",
  "chunk_index": 28
}
```

AST chunks additionally contain:

```json
{
  "node_type": "class_definition",
  "start_line": 908,
  "end_line": 920
}
```

Qdrant retrieval supports:

* top-k search
* cosine similarity
* repository filtering
* similarity thresholds
* metadata-aware retrieval

---

## Question Answering

After indexing, users can interact with the repository through the console.

Example:

```text
> Where is the Session class implemented?
```

The system:

```text
Question
   ↓
OpenAI embedding
   ↓
Qdrant similarity search
   ↓
Top relevant code chunks
   ↓
Context construction
   ↓
LLM
   ↓
Grounded answer
```

The LLM receives the retrieved repository context together with the user's question.

The prompt explicitly instructs the model to:

* answer using repository context
* explain relevant code clearly
* mention file paths when useful
* avoid unsupported claims

---

## Example

```text
==================================================
RepoRAG - AI Software Engineering Assistant
==================================================

Repository URL:
https://github.com/psf/requests.git

Preparing repository: requests...

Choose chunking strategy:
1. Language-aware
2. AST

Choice (1/2): 2
Using AST chunking.

Re-index repository? (y/n): y

Starting indexing...

==================================================
INDEXING COMPLETE
==================================================
Files:      65
Chunks:     ...

You can now ask questions about the repository.
Type 'exit' to quit.

> Where is the Session class implemented?
```

Example AST-based source output:

```text
Sources:
- src/requests/sessions.py#L908-L920
- tests/test_requests.py#L2608-L2638
- HISTORY.md#L1193-L1213
```

---

## Evaluation

RepoRAG includes a retrieval evaluation harness rather than relying only on subjective inspection of generated answers.

The evaluation dataset contains questions paired with expected source files, for example:

```text
Question:
Where is the Session class implemented?

Expected:
src/requests/sessions.py
```

The evaluator checks whether the expected file appears within the retrieved top-k results.

### Language-aware retrieval

The current evaluation achieved:

```text
Retrieval Accuracy: 95%
```

on the 20-question evaluation dataset used during development.

The metric represents **Hit@5-style source retrieval accuracy**: the expected source file appeared somewhere among the five retrieved results.

### AST retrieval

The AST evaluation separately measures:

```text
Hit@1
Hit@5
```

and additionally reports:

```text
file path
line range
AST node type
similarity score
```

This allows retrieval quality and citation quality to be inspected independently.

---

## Project Structure

```text
ai-swe/
│
├── app/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── indexing.py
│       └── chat.py
│
├── ingestion/
│   ├── cloner.py
│   ├── loader.py
│   ├── file_filter.py
│   ├── documents.py
│   ├── chunker.py
│   └── chunker_ast.py
│
├── rag/
│   ├── embeddings.py
│   ├── vector_store.py
│   └── generator.py
│
├── evals/
│   ├── dataset.py
│   ├── retrieval.py
│   └── ast_retrieval.py
│
├── tests/
│
├── repositories/
│
├── qdrant_data/
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Component             | Technology                  |
| --------------------- | --------------------------- |
| Language              | Python                      |
| LLM framework         | LangChain                   |
| LLM                   | OpenAI                      |
| Embeddings            | OpenAI Embeddings           |
| Vector database       | Qdrant                      |
| Code parsing          | Tree-sitter                 |
| Repository management | GitPython                   |
| Document processing   | LangChain Documents         |
| Text splitting        | LangChain Text Splitters    |
| Evaluation            | Custom retrieval evaluation |
| Interface             | Python CLI                  |

---

## Installation

### 1. Clone the project

```bash
git clone <your-repository-url>
cd ai-swe
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
```

Never commit `.env` to Git.

---

## Running RepoRAG

Start the console application:

```bash
python -m app
```

Enter a GitHub repository URL when prompted.

Then select the chunking strategy:

```text
1. Language-aware
2. AST
```

Choose whether to re-index the repository and start asking questions.

Exit with:

```text
exit
```

---

## Running Evaluations

Language-aware retrieval:

```bash
python -m evals.retrieval
```

AST retrieval:

```bash
python -m evals.ast_retrieval
```

The evaluation output reports retrieved files, similarity scores, and, for AST retrieval, line-level citations.

---

## Design Decisions

### Why Qdrant?

Qdrant provides vector similarity search together with payload metadata filtering. This allows RepoRAG to combine semantic retrieval with repository-level filtering.

### Why LangChain?

LangChain provides the document abstractions, language-aware text splitters, model integrations, and other components needed to assemble the RAG pipeline without hiding the underlying retrieval architecture.

### Why two chunking strategies?

Generic text splitting is simple and provides a strong baseline. AST-based chunking provides additional structural information and enables more precise source-level citations.

Keeping both strategies makes it possible to evaluate the trade-offs rather than assuming that structural chunking is automatically better.

### Why evaluate retrieval separately?

A generated answer can sound convincing even when the retriever returns incorrect context.

RepoRAG therefore evaluates retrieval independently by checking whether the expected source file appears among the retrieved results.

---

## Current Limitations

This version intentionally focuses on the RAG foundation.

Current limitations include:

* Console-only interface
* No persistent repository/user management layer
* No background indexing jobs
* No incremental indexing based on Git commits
* Retrieval evaluation is primarily source-file based
* AST retrieval quality varies by language and query
* No agentic tool-calling yet
* No multi-step investigation workflow
* No human-in-the-loop code modification
* No production deployment layer

These are intentional boundaries for the current milestone.

---

## Roadmap

The project is being developed incrementally.

```text
Current
  │
  ▼
Basic Repository RAG
  │
  ├── Language-aware chunking
  ├── AST chunking
  ├── Metadata filtering
  ├── Source citations
  └── Retrieval evaluation
  │
  ▼
FastAPI API
  │
  ▼
Tool-Calling Agent
  │
  ▼
Agentic RAG
  │
  ▼
LangGraph Orchestration
  │
  ▼
Software Engineering Workflows
  │
  ├── Explain
  ├── Debug
  ├── Code Review
  ├── Test Generation
  └── Architecture Analysis
  │
  ▼
Human-in-the-Loop
  │
  ▼
Production Deployment
```

The key architectural goal is to evolve the existing RAG system into an agentic software engineering assistant without replacing the underlying retrieval foundation.

---

## Project Status

**Current milestone: Repository RAG MVP**

Implemented:

* GitHub repository cloning
* Repository file ingestion
* File filtering
* LangChain document processing
* Language-aware chunking
* AST-based chunking
* OpenAI embeddings
* Qdrant vector storage
* Metadata filtering
* Similarity-based retrieval
* LLM-based question answering
* Source references
* AST line-level citations
* Retrieval evaluation
* Interactive console interface

The next architectural step is exposing these existing services through a FastAPI backend while keeping the RAG layer independent from the API layer.

---

## License

This project is intended as a personal software engineering and AI systems portfolio project.
