from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from app.config import LLMSettings


def create_llm(settings: LLMSettings) -> BaseChatModel:
    return ChatOpenAI(
        base_url=settings.base_url,
        model=settings.model,
        api_key=settings.api_key,
    )
