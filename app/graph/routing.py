from __future__ import annotations

import logging
import re
from typing import Callable

from app.agents.catalog import COPYWRITER, PUBLISHER
from app.graph.state import State

logger = logging.getLogger(__name__)

DECISION_RE = re.compile(r"^РЕШЕНИЕ:\s*(.+)$", re.MULTILINE)

# проверка вердикта редактора для запуска повторного цикла
def needs_revision(verdict: str) -> bool:
    match = DECISION_RE.search(verdict)
    if match:
        return "ДОРАБОТКУ" in match.group(1).upper()

    return "ТРЕБУЕТ ПЕРЕРАБОТКИ" in verdict.upper()


def make_editor_router(max_revisions: int) -> Callable[[State], str]:
    def route_after_editor(state: State) -> str:
        verdict = state["messages"][-1].content
        revisions_done = max(state["runs"].get(COPYWRITER, 1) - 1, 0)

        if not needs_revision(verdict):
            return PUBLISHER

        if revisions_done >= max_revisions:
            logger.warning(
                "Лимит доработок исчерпан (%s из %s), публикуем последнюю "
                "версию редактора",
                max_revisions,
                max_revisions,
            )
            return PUBLISHER

        logger.info("Круг доработки %s из %s", revisions_done + 1, max_revisions)
        return COPYWRITER

    return route_after_editor
