import os
from typing import Any
import dotenv
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

def invoke_openai_llm(prompt: str, config: Any = None):
    # print("[INVOKE][OPENAI_LLM]")

    # Create ChatOpenAI instance
    llm = get_openai_llm()

    # If structured output config provided, use structured output
    if config:
        # Use with_structured_output for structured responses
        structured_llm = llm.with_structured_output(config)
        response = structured_llm.invoke(prompt)
        return response
    else:
        # Regular invocation
        response = llm.invoke(prompt)
        return response.content


def get_openai_llm():
    # print("[GET][OPENAI_LLM]")

    return ChatOpenAI(
        model="gpt-4o",
        api_key=api_key,
        temperature=0
    )

