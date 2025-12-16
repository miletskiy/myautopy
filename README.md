# J.P. Morgan RAG Analysis: 2025 Forecast vs Mid-Year Reality

A LangGraph-based RAG system that compares J.P. Morgan's 2025 market forecast with mid-year 2025 actual results, focusing on stocks, investment themes, and valuation narratives.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Add PDF documents to data/pdfs/
# - outlook-2025-building-on-strength.pdf (Forecast)
# - mid-year-outlook-2025.pdf (Mid-Year Review)

# 4. Run the full pipeline
python main.py --all
```

## Project Structure

```
ahmad/
├── src/
│   ├── config.py              # Settings and configuration
│   ├── questions.py           # Pre-defined analysis questions
│   ├── ingestion/
│   │   ├── pdf_loader.py      # PDF text extraction (PyMuPDF)
│   │   └── chunker.py         # Semantic chunking logic
│   ├── retrieval/
│   │   └── vector_store.py    # ChromaDB vector store operations
│   ├── graph/
│   │   ├── nodes.py           # LangGraph node implementations
│   │   └── workflow.py        # Graph construction and execution
│   ├── prompts/
│   │   └── templates.py       # System and user prompts
│   └── schemas/
│       └── models.py          # Pydantic models
├── data/pdfs/                 # Place PDF documents here
├── outputs/                   # JSON analysis results
├── main.py                    # Entry point
└── requirements.txt
```

## Usage

### Full Pipeline
```bash
python main.py --all
```

### Individual Steps
```bash
# Ingest documents only
python main.py --ingest

# Re-ingest (force rebuild vector store)
python main.py --reingest

# Run analysis only (requires prior ingestion)
python main.py --analyze

# Ask a custom question
python main.py --question "What stocks were highlighted for 2025?"
```

## Design Choices

### 1. Chunking Strategy: Semantic Chunking

**Choice**: LangChain's `SemanticChunker` with embeddings-based breakpoints.

**Why**:
- Financial documents have varied paragraph lengths and complex structures
- Semantic chunking groups related sentences together, preserving context
- Better than fixed-size chunking for maintaining coherent investment narratives
- Uses percentile-based breakpoints (85th percentile) to balance chunk size and semantic coherence

**Trade-offs**:
- Slightly slower ingestion due to embedding computation during chunking
- More API calls during ingestion phase
- Variable chunk sizes (may affect retrieval consistency)

**Alternative considered**: Recursive character splitting with financial separators. Would be faster but loses semantic boundaries.

### 2. Routing Strategy: LLM-Based Router

**Choice**: GPT-4o-mini with structured output for routing decisions.

**Why**:
- Questions naturally fall into three categories: forecast-only, midyear-only, or comparison
- LLM can understand nuanced questions better than keyword matching
- Structured output ensures reliable parsing of routing decisions
- Reduces unnecessary retrieval (querying one doc when only one is needed)

**Implementation**:
```
Question → Router → Document Type (forecast/midyear/both)
                 → Retrieval filtered by document metadata
```

### 3. Vector Store: ChromaDB

**Choice**: ChromaDB with persistence.

**Why**:
- Lightweight, no server required
- Built-in metadata filtering (crucial for document-type routing)
- Good integration with LangChain
- Persistent storage avoids re-indexing on each run

**Trade-offs**:
- Not suitable for production scale (would need Pinecone, Weaviate, etc.)
- Limited advanced search features

### 4. Retrieval Strategy: Filtered Similarity Search

**Choice**: Similarity search with metadata filtering based on router decision.

**Why**:
- When router says "forecast", we only search forecast document
- When router says "both", we retrieve from both and merge results
- Improves precision by avoiding cross-document contamination
- `top_k=5` per document type ensures sufficient context

**Implementation**:
- Forecast-only: Filter by document name containing "outlook-2025-building"
- Midyear-only: Filter by document name containing "mid-year"
- Both: Parallel retrieval + merge + sort by score

### 5. Synthesis: Citation-Focused Generation

**Choice**: System prompt emphasizing strict grounding and citations.

**Why**:
- Financial analysis requires high accuracy
- Citations enable verification
- Explicit instructions to say "not mentioned" when information is missing
- Separates forecast claims from reality claims in comparisons

### 6. Embeddings: text-embedding-3-small

**Choice**: OpenAI's text-embedding-3-small.

**Why**:
- Good balance of cost and quality
- 1536 dimensions provides sufficient semantic resolution
- Fast inference
- Well-suited for financial text

**Alternative**: text-embedding-3-large for higher accuracy (but 3x cost).

## Limitations

1. **PDF Extraction Quality**: PyMuPDF extracts text but may lose some formatting, tables, and charts. Financial PDFs often have complex layouts.

2. **No Table/Chart Understanding**: Visual elements (charts, graphs) are not processed. Only textual content is indexed.

3. **Citation Granularity**: Citations are at page level. Finer-grained citations (paragraph/sentence) would require more sophisticated extraction.

4. **Single Retrieval Pass**: The system does a single retrieval. Iterative retrieval or query decomposition could improve complex question handling.

5. **No Reranking**: Retrieved chunks are ranked by embedding similarity only. A cross-encoder reranker could improve precision.

6. **Context Window**: With semantic chunking, chunk sizes vary. Very long chunks may be truncated. Consider implementing chunk size limits.

## Potential Improvements (with time estimates)

1. **Add Reranking** (~1-2 hours)
   - Use Cohere Rerank or cross-encoder to re-score retrieved chunks
   - Improves precision for complex queries

2. **Iterative Retrieval** (~2-3 hours)
   - If initial retrieval doesn't answer the question, decompose and re-query
   - Useful for multi-part questions

3. **Table Extraction** (~2-3 hours)
   - Use specialized table extraction (e.g., Camelot, Tabula)
   - Store tables separately with structured metadata

4. **Evaluation Framework** (~1-2 hours)
   - Add RAGAS or similar evaluation metrics
   - Create ground truth QA pairs for automated testing

5. **Caching Layer** (~1 hour)
   - Cache LLM responses for identical questions
   - Reduces cost for repeated queries

## Output Format

Results are saved to `outputs/analysis_results_YYYYMMDD_HHMMSS.json`:

```json
{
  "metadata": {
    "generated_at": "2025-01-15T10:30:00",
    "model": "gpt-4o-mini",
    "embedding_model": "text-embedding-3-small",
    "chunk_size": 1000,
    "top_k": 5
  },
  "results": {
    "Q1": {
      "id": "Q1",
      "title": "Forecasted Equity Themes",
      "question": "...",
      "routing": {
        "document_type": "forecast",
        "reasoning": "..."
      },
      "answer": "...",
      "citations": [
        {
          "document": "outlook-2025-building-on-strength",
          "page": 5,
          "text_excerpt": "..."
        }
      ],
      "retrieved_chunks_count": 5
    }
  }
}
```

## Requirements

- Python 3.12+
- OpenAI API key
- ~50MB disk space for vector store
