from __future__ import annotations

import json
import os
import re
from typing import Any

from .utils import load_dotenv


DEFAULT_MODEL = "gemini-3.5-flash"


class GeminiUnavailable(RuntimeError):
    pass


def _load_client() -> Any:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiUnavailable("GEMINI_API_KEY is not set.")
    try:
        from google import genai
    except Exception as exc:
        raise GeminiUnavailable("The google-genai package is not installed.") from exc
    return genai.Client(api_key=api_key)


def configured_model(default: str = DEFAULT_MODEL) -> str:
    load_dotenv()
    return os.getenv("GEMINI_MODEL", default)


def extract_json(text: str) -> Any:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\}|\[.*\])", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(1))


def generate_json(prompt: str, model: str | None = None) -> Any:
    client = _load_client()
    selected_model = model or configured_model()
    try:
        response = client.models.generate_content(
            model=selected_model,
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
    except TypeError:
        response = client.models.generate_content(model=selected_model, contents=prompt)
    return extract_json(response.text or "")
