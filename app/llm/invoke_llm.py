import json
import os
from typing import Any
import dotenv
# import google.genai as genai
from google import genai

dotenv.load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

def invoke_llm(prompt: str, config: Any = None, model: str = None):
    print("[INVOKE][LLM]")

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
    print(type(parsed_response))

    return parsed_response


# client = Client("huggingface-projects/llama-3.2-3B-Instruct")
# result = client.predict(
#     message=prompt,
#     max_new_tokens=256,
#     temperature=0.6,
#     top_p=0.9,
#     top_k=50,
#     repetition_penalty=1.2,
#     api_name="/chat"
# )
        