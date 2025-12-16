from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from loguru import logger

from src.config import settings
from src.schemas.models import DocumentType, RetrievedChunk


def get_embeddings() -> OpenAIEmbeddings:
    """Get OpenAI embeddings instance."""
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key,
    )


def create_vector_store(
    documents: list[Document],
    embeddings: OpenAIEmbeddings,
    persist_directory: Path | None = None,
) -> Chroma:
    """
    Create a ChromaDB vector store from documents.
    """
    persist_dir = persist_directory or settings.chroma_dir

    logger.info(f"Creating vector store with {len(documents)} documents")
    logger.info(f"Persist directory: {persist_dir}")

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(persist_dir),
        collection_name="jpmorgan_outlook",
    )

    logger.info("Vector store created successfully")
    return vector_store


def load_vector_store(
    embeddings: OpenAIEmbeddings,
    persist_directory: Path | None = None,
) -> Chroma:
    """
    Load an existing ChromaDB vector store.
    """
    persist_dir = persist_directory or settings.chroma_dir

    logger.info(f"Loading vector store from {persist_dir}")

    vector_store = Chroma(
        persist_directory=str(persist_dir),
        embedding_function=embeddings,
        collection_name="jpmorgan_outlook",
    )

    return vector_store


def retrieve_chunks(
    vector_store: Chroma,
    query: str,
    document_type: DocumentType,
    top_k: int | None = None,
) -> list[RetrievedChunk]:
    """
    Retrieve relevant chunks from the vector store based on document type.

    Args:
        vector_store: The ChromaDB vector store
        query: The search query
        document_type: Which document(s) to search (forecast, midyear, or both)
        top_k: Number of results to return (defaults to settings.top_k)

    Returns:
        List of RetrievedChunk objects with content, metadata, and scores
    """
    k = top_k or settings.top_k

    if document_type == DocumentType.BOTH:
        results_forecast = vector_store.similarity_search_with_score(
            query,
            k=k,
            filter={"doc_type": {"$eq": "forecast"}},
        )
        results_midyear = vector_store.similarity_search_with_score(
            query,
            k=k,
            filter={"doc_type": {"$eq": "midyear"}},
        )
        results = results_forecast + results_midyear
        results = sorted(results, key=lambda x: x[1])[: k * 2]
    elif document_type == DocumentType.FORECAST:
        results = vector_store.similarity_search_with_score(
            query,
            k=k,
            filter={"doc_type": {"$eq": "forecast"}},
        )
    elif document_type == DocumentType.MIDYEAR:
        results = vector_store.similarity_search_with_score(
            query,
            k=k,
            filter={"doc_type": {"$eq": "midyear"}},
        )
    else:
        results = vector_store.similarity_search_with_score(query, k=k)

    chunks = []
    for doc, score in results:
        chunk = RetrievedChunk(
            content=doc.page_content,
            document=doc.metadata.get("document", "unknown"),
            page=doc.metadata.get("page", 0),
            score=float(score),
        )
        chunks.append(chunk)

    logger.info(
        f"Retrieved {len(chunks)} chunks for query: '{query[:50]}...' "
        f"(document_type={document_type})"
    )

    return chunks
