"""
J.P. Morgan RAG Analysis: 2025 Forecast vs Mid-Year Reality

This script runs the complete RAG pipeline:
1. Loads and chunks PDF documents
2. Creates/loads vector store
3. Runs predefined questions through the LangGraph workflow
4. Outputs results to JSON
"""

import sys

from loguru import logger

from src.config import settings
from src.ingestion.pdf_loader import load_all_pdfs

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

    print(docs_by_name)

    logger.info("Document ingestion complete")


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

    args = parser.parse_args()

    if args.ingest:
        ingest_documents(force_reingest=True)
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python main.py --ingest           # Only ingest documents")


if __name__ == "__main__":
    main()
