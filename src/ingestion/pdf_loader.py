from pathlib import Path

import fitz
from langchain_core.documents import Document
from loguru import logger


def classify_document_type(doc_name: str) -> str:
    """
    Classify document as 'forecast' or 'midyear' based on filename.
    """
    doc_name_lower = doc_name.lower()
    if "mid-year" in doc_name_lower or "midyear" in doc_name_lower:
        return "midyear"
    return "forecast"


def extract_text_from_pdf(pdf_path: Path) -> list[Document]:
    """
    Extract text from PDF using PyMuPDF, preserving page-level metadata.

    Returns a list of LangChain Documents, one per page.
    """
    documents = []
    doc_name = pdf_path.stem
    doc_type = classify_document_type(doc_name)

    logger.info(f"Loading PDF: {pdf_path} (type: {doc_type})")

    with fitz.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf, start=1):
            text = page.get_text("text")

            if text.strip():
                doc = Document(
                    page_content=text,
                    metadata={
                        "source": str(pdf_path),
                        "document": doc_name,
                        "doc_type": doc_type,
                        "page": page_num,
                        "total_pages": len(pdf),
                    },
                )
                documents.append(doc)

    logger.info(f"Extracted {len(documents)} pages from {doc_name}")
    return documents


def load_all_pdfs(data_dir: Path) -> dict[str, list[Document]]:
    """
    Load all PDFs from the data directory.

    Returns a dictionary mapping document names to their page documents.
    """
    all_docs = {}

    pdf_files = list(data_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files in {data_dir}")

    for pdf_path in pdf_files:
        docs = extract_text_from_pdf(pdf_path)
        all_docs[pdf_path.stem] = docs

    return all_docs
