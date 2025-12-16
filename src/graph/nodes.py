from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from loguru import logger

from src.config import settings
from src.prompts.templates import (
    ROUTER_SYSTEM_PROMPT,
    ROUTER_USER_PROMPT,
    SYNTHESIS_SYSTEM_PROMPT,
    SYNTHESIS_USER_PROMPT,
)
from src.retrieval.vector_store import retrieve_chunks
from src.schemas.models import (
    AnswerWithCitations,
    Citation,
    DocumentType,
    GraphState,
    RouterDecision,
)


def get_llm() -> ChatOpenAI:
    """Get the LLM instance."""
    return ChatOpenAI(
        model=settings.llm_model,
        temperature=0,
        openai_api_key=settings.openai_api_key,
    )


def router_node(state: GraphState) -> dict:
    """
    Router node that decides which document(s) to query.

    Uses structured output to get a reliable routing decision.
    """
    logger.info(f"Router processing question: {state.question[:100]}...")

    llm = get_llm()
    structured_llm = llm.with_structured_output(RouterDecision)

    messages = [
        SystemMessage(content=ROUTER_SYSTEM_PROMPT),
        HumanMessage(content=ROUTER_USER_PROMPT.format(question=state.question)),
    ]

    decision: RouterDecision = structured_llm.invoke(messages)

    logger.info(f"Router decision: {decision.document_type} - {decision.reasoning}")

    return {
        "document_type": decision.document_type,
        "routing_reasoning": decision.reasoning,
    }


def create_retrieval_node(vector_store: Chroma):
    """
    Factory function that creates a retrieval node with access to the vector store.
    """

    def retrieval_node(state: GraphState) -> dict:
        """
        Retrieval node that fetches relevant chunks from the vector store.
        """
        logger.info(f"Retrieving chunks for document_type={state.document_type}")

        chunks = retrieve_chunks(
            vector_store=vector_store,
            query=state.question,
            document_type=state.document_type,
            top_k=settings.top_k,
        )

        logger.info(f"Retrieved {len(chunks)} chunks")

        return {"retrieved_chunks": chunks}

    return retrieval_node


def synthesis_node(state: GraphState) -> dict:
    """
    Synthesis node that generates an answer from retrieved chunks.

    Produces a structured response with citations.
    """
    logger.info("Synthesizing answer from retrieved chunks")

    context_parts = []
    for chunk in state.retrieved_chunks:
        context_parts.append(
            f"[{chunk.document}, Page {chunk.page}]\n{chunk.content}\n"
        )

    context = "\n---\n".join(context_parts)

    llm = get_llm()

    messages = [
        SystemMessage(content=SYNTHESIS_SYSTEM_PROMPT),
        HumanMessage(
            content=SYNTHESIS_USER_PROMPT.format(
                context=context,
                question=state.question,
            )
        ),
    ]

    response = llm.invoke(messages)
    answer_text = response.content

    citations = []
    for chunk in state.retrieved_chunks:
        citation = Citation(
            document=chunk.document,
            page=chunk.page,
            text=(
                chunk.content[:200] + "..."
                if len(chunk.content) > 200
                else chunk.content
            ),
        )
        citations.append(citation)

    answer = AnswerWithCitations(
        answer=answer_text,
        citations=citations,
    )

    logger.info("Answer synthesized successfully")

    return {"answer": answer}
