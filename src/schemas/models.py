from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    FORECAST = "forecast"
    MIDYEAR = "midyear"
    BOTH = "both"


class Citation(BaseModel):
    document: str = Field(description="Document name (forecast or midyear)")
    page: int = Field(description="Page number in the document")
    text: str = Field(description="Exact quoted text from the document")


class AnswerWithCitations(BaseModel):
    answer: str = Field(description="The answer to the question")
    citations: list[Citation] = Field(
        default_factory=list, description="Citations supporting the answer"
    )


class RouterDecision(BaseModel):
    document_type: DocumentType = Field(
        description="Which document(s) to query: forecast, midyear, or both"
    )
    reasoning: str = Field(description="Brief explanation of the routing decision")


class RetrievedChunk(BaseModel):
    content: str
    document: str
    page: int
    score: float


class GraphState(BaseModel):
    question: str
    document_type: DocumentType | None = None
    routing_reasoning: str = ""
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    answer: AnswerWithCitations | None = None


class StockThemeComparison(BaseModel):
    stock_or_theme: str = Field(description="Name of the stock or investment theme")
    forecast_view: str = Field(description="What was stated/implied in 2025 forecast")
    midyear_reality: str = Field(description="What happened by mid-year 2025")
    supported: Literal["Yes", "No", "Partially", "Not Mentioned"] = Field(
        description="Whether the forecast was supported by mid-year reality"
    )
    citation: str = Field(description="Document and page references")


class StructuredComparisonOutput(BaseModel):
    comparisons: list[StockThemeComparison] = Field(
        description="List of stock/theme comparisons"
    )
