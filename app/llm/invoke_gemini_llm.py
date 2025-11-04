import json
import os
from typing import Any
import dotenv
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI

dotenv.load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

def invoke_gemini_llm(prompt: str, config: Any = None, model: str = None):
    if model is None:
        model = "gemini-2.5-flash"

    if config is None:
        config = {}

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": config,
        },
    )

    parsed_response = json.loads(response.text)
    return parsed_response


def get_gemini_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.7
    )

