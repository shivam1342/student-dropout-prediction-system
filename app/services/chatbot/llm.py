"""Groq LLM wrapper for LangChain compatibility."""
from __future__ import annotations

import os
from typing import Any, List, Optional

from langchain_core.language_models.llms import LLM
from pydantic import PrivateAttr

from app.services.chatbot.config import GROQ_MODEL, GROQ_TEMPERATURE


class GroqLLM(LLM):
    """Minimal LangChain-compatible LLM wrapper around Groq Chat Completions."""

    _client: Any = PrivateAttr(default=None)

    def __init__(self, api_key: Optional[str] = None, **kwargs: Any):
        super().__init__(**kwargs)
        key = api_key or os.getenv("GROQ_API_KEY")
        if isinstance(key, str):
            key = key.strip().strip("\"").strip("'")
        if not key:
            raise ValueError("GROQ_API_KEY is not configured")

        try:
            from groq import Groq
        except Exception as exc:
            raise ImportError("groq package is required for chatbot LLM") from exc

        self._client = Groq(api_key=key)

    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any) -> str:
        response = self._client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a student counsellor."},
                {"role": "user", "content": prompt},
            ],
            temperature=GROQ_TEMPERATURE,
        )
        return response.choices[0].message.content or ""

    @property
    def _llm_type(self) -> str:
        return "groq"
