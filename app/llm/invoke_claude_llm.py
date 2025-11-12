import os
from typing import Any, Optional
import dotenv
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel

dotenv.load_dotenv()

def invoke_claude_llm(prompt: str, config: Any = None, model: Optional[str] = None) -> Any:
    """
    Invoke Claude LLM with optional structured output.

    Args:
        prompt: Prompt string to send to the LLM
        config: Optional Pydantic BaseModel for structured output
        model: Optional model name (default: claude-3-5-sonnet-20240620)

    Returns:
        - If config is provided: Pydantic model instance
        - If config is None: string response
    """
    print("[INVOKE][CLAUDE_LLM]")

    llm = _get_claude_llm(model)

    if config:
        structured_llm = llm.with_structured_output(config)
        response = structured_llm.invoke(prompt)
        return response
    else:
        response = llm.invoke(prompt)
        return response.content


def _get_claude_llm(model: Optional[str] = None):
    """Private function to create a ChatAnthropic instance."""
    if model is None:
        model = "claude-sonnet-4-5-20250929"

    return ChatAnthropic(
        model_name=model,
        timeout=None,
        stop=None,
    )


def get_claude_llm(model: Optional[str] = None):
    """Public accessor for Claude LLM instance."""
    print("[GET][CLAUDE_LLM]")
    return _get_claude_llm(model)
