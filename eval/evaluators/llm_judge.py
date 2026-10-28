import os
import json
import time
from google import genai
from google.genai import types

JUDGE_PROMPT = """You are an impartial evaluation judge. Analyze the provided context and the agent's answer.
Grade the answer based solely on whether it is fully grounded in the context without fabricating unverified facts.

Context:
{context}

Generated Answer:
{answer}

Respond ONLY with a JSON object: {{"score": <float between 0.0 and 1.0>, "reason": "<brief justification>"}}
"""

def evaluate_faithfulness(context: list, answer: str, max_retries: int = 3) -> dict:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return {"score": 1.0, "reason": "No API key configured."}

    client = genai.Client(api_key=gemini_key)
    prompt = JUDGE_PROMPT.format(
        context="\n---\n".join(context) if context else "No context provided.",
        answer=answer
    )
    model_name = os.getenv("EVAL_JUDGE_MODEL", "gemini-3.8-flash")

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                time.sleep(2 ** attempt)
            else:
                return {"score": 0.0, "reason": f"Judge error: {str(e)}"}

    return {"score": 0.0, "reason": "Judge failed due to upstream 503."}