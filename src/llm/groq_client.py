"""
Thin wrapper around langchain-groq for LLM calls.
Centralizes model config so every caller (brief parser, reasoning
generator) uses the same client setup.
"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import GROQ_API_KEY, LLM_MODEL_NAME, LLM_TEMPERATURE

_llm = None


def get_llm() -> ChatGroq:
    """Lazily initialize the Groq LLM client (singleton)."""
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=LLM_MODEL_NAME,
            temperature=LLM_TEMPERATURE,
        )
    return _llm


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Send a system + user message pair to the LLM and return raw text.
    Callers are responsible for parsing/cleaning the output
    (see src/utils/output_parser.py).
    """
    llm = get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    response = llm.invoke(messages)
    return response.content