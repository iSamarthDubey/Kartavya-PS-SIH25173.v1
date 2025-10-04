"""
RAG Pipeline module for intelligent document retrieval and generation.

Components:
- RAGPipeline: Main RAG orchestrator
- DocumentRetriever: Retrieve relevant documents
- VectorStore: Vector database interface
- PromptBuilder: Build LLM prompts
"""

__version__ = "1.0.0"

try:
    from .pipeline import RAGPipeline
    from .retriever import DocumentRetriever
    from .vector_store import VectorStore
    from .prompt_builder import PromptBuilder
    
    __all__ = [
        'RAGPipeline',
        'DocumentRetriever',
        'VectorStore',
        'PromptBuilder',
    ]
except ImportError:
    __all__ = []
