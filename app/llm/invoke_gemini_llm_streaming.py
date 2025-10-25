import json
import os
from typing import Any, Generator
import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

dotenv.load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

def invoke_gemini_llm_streaming(prompt: str, config: Any = None, model: str = None):
    """
    Invoke Gemini LLM with streaming output.

    Args:
        prompt: The prompt to send to the LLM
        config: Optional response schema for structured output
        model: Optional model name (defaults to gemini-2.5-flash)

    Returns:
        Parsed JSON response or raw text
    """
    print("[INVOKE][GEMINI_LLM][STREAMING]")

    if model is None:
        model = "gemini-2.5-flash"

    if config is None:
        config = {}

    # Initialize ChatGoogleGenerativeAI with streaming enabled
    # Include model_kwargs in initialization if config is provided
    if config:
        llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.7,
            model_kwargs={
                "response_mime_type": "application/json",
                "response_schema": config,
            }
        )
    else:
        llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.7
        )

    # Stream the response
    full_response = ""
    for chunk in llm.stream(prompt):
        content = chunk.content
        print(content, end="", flush=True)
        full_response += content

    print()  # New line after streaming

    # Parse response if it's JSON
    # Strip markdown code fences if present
    response_to_parse = full_response.strip()
    if response_to_parse.startswith("```json"):
        response_to_parse = response_to_parse[7:]  # Remove ```json
    if response_to_parse.startswith("```"):
        response_to_parse = response_to_parse[3:]  # Remove ```
    if response_to_parse.endswith("```"):
        response_to_parse = response_to_parse[:-3]  # Remove trailing ```
    response_to_parse = response_to_parse.strip()

    try:
        parsed_response = json.loads(response_to_parse)
        print(type(parsed_response))
        return parsed_response
    except json.JSONDecodeError as e:
        print(f"[WARN] Failed to parse JSON: {e}")
        return full_response
