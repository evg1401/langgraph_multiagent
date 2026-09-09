from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import os

from dotenv import load_dotenv

from app.personas import NETWORKS

DEFAULT_MAX_REVISIONS = 3


class ConfigError(RuntimeError):
    """Конфигурации не хватает данных для запуска."""


def _require(missing: Sequence[str]) -> None:
    if missing:
        raise ConfigError(
            f"Не заданы переменные окружения: {', '.join(missing)}"
        )


@dataclass(frozen=True)
class LLMSettings:
    api_key: str | None = None
    base_url: str | None = None
    model: str | None = None

    def missing(self) -> list[str]:
        return [
            name
            for name, value in (
                ("LLM_API_KEY", self.api_key),
                ("LLM_BASE_URL", self.base_url),
                ("LLM_MODEL", self.model),
            )
            if not value
        ]


@dataclass(frozen=True)
class LangfuseSettings:
    public_key: str | None = None
    secret_key: str | None = None
    base_url: str | None = None

    @property
    def configured(self) -> bool:
        return bool(self.public_key and self.secret_key and self.base_url)


@dataclass(frozen=True)
class Settings:
    llm: LLMSettings = LLMSettings()
    langfuse: LangfuseSettings = LangfuseSettings()
    network: str | None = None
    brief_file: str | None = None
    max_revisions: int = DEFAULT_MAX_REVISIONS

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        if env is None:
            load_dotenv()
            env = os.environ

        return cls(
            llm=LLMSettings(
                api_key=env.get("LLM_API_KEY"),
                base_url=env.get("LLM_BASE_URL"),
                model=env.get("LLM_MODEL"),
            ),
            langfuse=LangfuseSettings(
                public_key=env.get("LANGFUSE_PUBLIC_KEY"),
                secret_key=env.get("LANGFUSE_SECRET_KEY"),
                base_url=env.get("LANGFUSE_BASE_URL"),
            ),
            network=env.get("TARGET_NETWORK"),
            brief_file=env.get("BRIEF_FILE"),
        )

    def validate(self) -> None:
        missing = self.llm.missing()
        if not self.network:
            missing.append("TARGET_NETWORK")
        _require(missing)

        if self.network not in NETWORKS:
            raise ConfigError(
                f"TARGET_NETWORK «{self.network}» не поддерживается. "
                f"Доступны: {', '.join(NETWORKS)}"
            )
