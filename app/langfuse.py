from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from app.config import LangfuseSettings

logger = logging.getLogger(__name__)


def new_session_id(prefix: str) -> str:
    return f"{prefix}-{datetime.now():%Y%m%d-%H%M%S}"


def create_langfuse_handler(settings: LangfuseSettings) -> tuple[Any | None, Any | None]:
    if not settings.configured:
        logger.info(
            "переменные окружения не заданы — langfuse отключен"
        )
        
        return None, None

    try:
        from langfuse import Langfuse
        from langfuse.langchain import CallbackHandler
    except ImportError as exc:
        logger.warning(
            "интеграция Langfuse недоступна (%s)",
            exc,
        )

        return None, None

    client = Langfuse(
        public_key=settings.public_key,
        secret_key=settings.secret_key,
        base_url=settings.base_url,
    )

    try:
        authorized = client.auth_check()
    except Exception as exc:
        logger.warning(
            "auth_check не прошёл (%s) — проверьте ключи "
            "langfuse отключен",
            exc.__class__.__name__,
        )

        return None, None

    if not authorized:
        logger.warning(
            "auth_check вернул False — проверьте ключи, "
            "langfuse отключен"
        )

        return None, None

    logger.info("Трассировка включена: %s", settings.base_url)
    return client, CallbackHandler(public_key=settings.public_key)
