from langchain_chroma import Chroma
from langgraph.graph import END, StateGraph
from loguru import logger

from src.graph.nodes import (
    create_retrieval_node,
    router_node,
    synthesis_node,
)
from src.schemas.models import GraphState


def build_rag_graph(vector_store: Chroma) -> StateGraph:
    """
    Build the LangGraph RAG workflow.

    The graph has the following structure:
    1. Router Node - Decides which document(s) to query
    2. Retrieval Node - Fetches relevant chunks from vector store
    3. Synthesis Node - Generates answer with citations

    Flow: START -> router -> retrieval -> synthesis -> END
    """
    logger.info("Building RAG graph")

    workflow = StateGraph(GraphState)

    workflow.add_node("router", router_node)
    workflow.add_node("retrieval", create_retrieval_node(vector_store))
    workflow.add_node("synthesis", synthesis_node)

    workflow.set_entry_point("router")

    workflow.add_edge("router", "retrieval")
    workflow.add_edge("retrieval", "synthesis")
    workflow.add_edge("synthesis", END)

    graph = workflow.compile()

    logger.info("RAG graph compiled successfully")

    return graph


def run_query(graph: StateGraph, question: str) -> GraphState:
    """
    Run a query through the RAG graph.

    Args:
        graph: The compiled LangGraph workflow
        question: The user's question

    Returns:
        The final GraphState with the answer and citations
    """
    logger.info(f"Running query: {question[:100]}...")

    initial_state = GraphState(question=question)

    result = graph.invoke(initial_state)

    final_state = GraphState(**result)

    logger.info("Query completed")

    return final_state
