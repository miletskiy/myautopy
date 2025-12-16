"""
J.P. Morgan RAG Analysis: 2025 Forecast vs Mid-Year Reality

This script runs the complete RAG pipeline:
1. Loads and chunks PDF documents
2. Creates/loads vector store
3. Runs predefined questions through the LangGraph workflow
4. Outputs results to JSON
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger

from src.config import settings
from src.graph.workflow import build_rag_graph, run_query
from src.ingestion.chunker import chunk_all_documents
from src.ingestion.pdf_loader import load_all_pdfs
from src.questions import QUESTIONS
from src.retrieval.vector_store import (
    create_vector_store,
    get_embeddings,
    load_vector_store,
)

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    level="INFO",
)


def ingest_documents(force_reingest: bool = False) -> None:
    """
    Ingest PDF documents into the vector store.

    Args:
        force_reingest: If True, re-ingest even if vector store exists
    """
    if settings.chroma_dir.exists() and not force_reingest:
        logger.info(
            "Vector store already exists. Use --reingest to force re-ingestion."
        )
        return

    logger.info("Starting document ingestion")

    if not settings.data_dir.exists():
        logger.error(f"Data directory not found: {settings.data_dir}")
        logger.error("Please place the PDF files in the data/pdfs/ directory")
        sys.exit(1)

    pdf_files = list(settings.data_dir.glob("*.pdf"))
    if len(pdf_files) < 2:
        logger.error(
            f"Expected 2 PDF files, found {len(pdf_files)}. "
            "Please ensure both Outlook 2025 and Mid-Year Outlook 2025 PDFs are in data/pdfs/"
        )
        sys.exit(1)

    docs_by_name = load_all_pdfs(settings.data_dir)

    embeddings = get_embeddings()

    all_chunks = chunk_all_documents(docs_by_name, embeddings, use_semantic=True)

    create_vector_store(all_chunks, embeddings)

    logger.info("Document ingestion complete")


def run_analysis() -> dict:
    """
    Run all predefined questions and return results.

    Returns:
        Dictionary with question IDs as keys and results as values
    """
    logger.info("Starting RAG analysis")

    embeddings = get_embeddings()
    vector_store = load_vector_store(embeddings)

    graph = build_rag_graph(vector_store)

    results = {}

    for q_id, q_data in QUESTIONS.items():
        logger.info(f"Processing {q_id}: {q_data['title']}")

        state = run_query(graph, q_data["question"])

        results[q_id] = {
            "id": q_id,
            "title": q_data["title"],
            "question": q_data["question"],
            "routing": {
                "document_type": (
                    state.document_type.value if state.document_type else None
                ),
                "reasoning": state.routing_reasoning,
            },
            "answer": state.answer.answer if state.answer else None,
            "citations": [
                {
                    "document": c.document,
                    "page": c.page,
                    "text_excerpt": c.text,
                }
                for c in (state.answer.citations if state.answer else [])
            ],
            "retrieved_chunks_count": len(state.retrieved_chunks),
        }

        logger.info(f"Completed {q_id}")

    return results


def save_results(results: dict) -> Path:
    """
    Save results to a JSON file.

    Returns:
        Path to the saved file
    """
    settings.outputs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = settings.outputs_dir / f"analysis_results_{timestamp}.json"

    output_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "model": settings.llm_model,
            "embedding_model": settings.embedding_model,
            "chunk_size": settings.chunk_size,
            "top_k": settings.top_k,
        },
        "results": results,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to {output_file}")

    return output_file


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="J.P. Morgan RAG Analysis: 2025 Forecast vs Mid-Year Reality"
    )
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Ingest PDF documents into vector store",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Run analysis with predefined questions",
    )
    args = parser.parse_args()

    if args.ingest:
        ingest_documents(force_reingest=True)
    elif args.analyze:
        results = run_analysis()
        save_results(results)
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python main.py --ingest           # Only ingest documents")
        print("  python main.py --analyze          # Only run analysis")


if __name__ == "__main__":
    main()
