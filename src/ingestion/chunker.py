from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger

from src.config import settings


def create_semantic_chunker(embeddings: OpenAIEmbeddings) -> SemanticChunker:
    """
    Create a semantic chunker that splits based on embedding similarity.

    This approach creates more meaningful chunks by grouping semantically
    related sentences together, rather than splitting at arbitrary character counts.
    """
    return SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=85,
    )


def create_recursive_chunker() -> RecursiveCharacterTextSplitter:
    """
    Fallback chunker using recursive character splitting.

    Used when semantic chunking fails or for very short documents.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )


def chunk_documents(
    documents: list[Document],
    embeddings: OpenAIEmbeddings,
    use_semantic: bool = True,
) -> list[Document]:
    """
    Chunk documents using semantic or recursive chunking.

    Preserves metadata from original documents and adds chunk-specific metadata.
    """
    if not documents:
        return []

    chunked_docs = []

    if use_semantic:
        logger.info("Using semantic chunking")
        chunker = create_semantic_chunker(embeddings)
    else:
        logger.info("Using recursive character chunking")
        chunker = create_recursive_chunker()

    for doc in documents:
        try:
            if use_semantic:
                chunks = chunker.create_documents(
                    [doc.page_content],
                    metadatas=[doc.metadata],
                )
            else:
                chunks = chunker.split_documents([doc])

            for i, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = i
                chunk.metadata["total_chunks_in_page"] = len(chunks)
                chunked_docs.append(chunk)

        except Exception as e:
            logger.warning(
                f"Semantic chunking failed for page {doc.metadata.get('page')}: {e}. "
                "Falling back to recursive chunking."
            )
            fallback_chunker = create_recursive_chunker()
            chunks = fallback_chunker.split_documents([doc])
            for i, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = i
                chunk.metadata["total_chunks_in_page"] = len(chunks)
                chunked_docs.append(chunk)

    logger.info(f"Created {len(chunked_docs)} chunks from {len(documents)} pages")
    return chunked_docs


def chunk_all_documents(
    docs_by_name: dict[str, list[Document]],
    embeddings: OpenAIEmbeddings,
    use_semantic: bool = True,
) -> list[Document]:
    """
    Chunk all documents from multiple PDFs.

    Returns a flat list of all chunks with preserved metadata.
    """
    all_chunks = []

    for doc_name, docs in docs_by_name.items():
        logger.info(f"Chunking document: {doc_name}")
        chunks = chunk_documents(docs, embeddings, use_semantic)
        all_chunks.extend(chunks)

    logger.info(f"Total chunks across all documents: {len(all_chunks)}")
    return all_chunks
