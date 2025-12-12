"""
LLM handler module for language model initialization and queries.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from config import LLM_MODEL


def initialize_llm():
    """Initialize the language model."""
    return ChatGoogleGenerativeAI(model=LLM_MODEL)


def query_llm(llm, user_query, context):
    """Query the LLM with context from retrieved documents."""
    messages = [
        (
            "system",
            "You are a helpful assistant that can answer questions about a given topic based on the provided context.",
        ),
        ("human", f"Context: {context}\n\nQuestion: {user_query}"),
    ]

    response = llm.invoke(messages)
    return response.content
