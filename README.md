# AI Software Engineering Assistant

An AI assistant that can understand and answer questions about GitHub repositories using Retrieval-Augmented Generation (RAG).

The system clones a GitHub repository, filters relevant source files, creates code-aware chunks, generates embeddings, stores them in Qdrant, and retrieves relevant code to answer natural-language questions.

## Current Stage

**M2 - Code-Aware Repository RAG**

## Current Features

- Clone GitHub repositories using GitPython
- Filter irrelevant files and directories
- Convert source files into LangChain Documents
- Language-aware code chunking using LangChain
- Tree-sitter AST-based code chunking
- Repository and file metadata attached to chunks
- OpenAI embeddings for semantic search
- Qdrant vector storage
- Repository-level metadata filtering
- Similarity score thresholding
- Top-k semantic retrieval
- Custom retrieval evaluation
- Console-based RAG testing

## RAG Pipeline

```text
GitHub Repository
       ↓
   Clone Repo
       ↓
   File Filtering
       ↓
  Document Loading
       ↓
   Code Chunking
       ↓
 OpenAI Embeddings
       ↓
      Qdrant
       ↓
  Semantic Retrieval
       ↓
      LLM
       ↓
     Answer