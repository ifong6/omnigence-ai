import os
from typing import Any, TypeVar, overload
import dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

dotenv.load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')


def invoke_openai_llm(prompt: str, config: Any = None) -> Any:
    # Create ChatOpenAI instance
    llm = _get_openai_llm()

    # If structured output config provided, use structured output
    if config:
        # Use with_structured_output for structured responses
        # Returns a Pydantic model object directly
        structured_llm = llm.with_structured_output(config)
        response = structured_llm.invoke(prompt)
        return response
    else:
        # Regular invocation
        response = llm.invoke(prompt)
        return response.content


def _get_openai_llm():
    return ChatOpenAI(
        model="gpt-4o",
        api_key=api_key,
        temperature=0
    )


def get_openai_llm():
    """Public function to get OpenAI LLM instance."""
    return _get_openai_llm()

