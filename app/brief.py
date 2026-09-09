from __future__ import annotations

from pathlib import Path

class BriefError(RuntimeError):
    """Бриф не удалось прочитать."""


def load_brief(path: str) -> str:
    source = Path(path)

    try:
        content = source.read_text(encoding="utf-8")
    except OSError as exc:
        raise BriefError(f"Не удалось прочитать бриф из «{source}»: {exc}") from exc

    brief = content.strip()
    if not brief:
        raise BriefError(f"Бриф пуст: файл «{source}»")

    return brief
