from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import BaseMessage

from app.agents.catalog import COPYWRITER, build_agents
from app.config import Settings
from app.graph import build_graph, initial_state
from app.llm import create_llm
from app.langfuse import new_session_id

logger = logging.getLogger(__name__)

RUN_NAME = "smm-multiagents"


@dataclass(frozen=True)
class RunResult:
    # итог прогона
    messages: list[BaseMessage] = field(default_factory=list)
    runs: dict[str, int] = field(default_factory=dict)
    network: str = ""

    @property
    # кол-во циклов отработано
    def revisions(self) -> int:
        return max(self.runs.get(COPYWRITER, 1) - 1, 0)

    @property
     # последнее сообщение диалога
    def final_text(self) -> str:
        return self.messages[-1].content if self.messages else ""


class ContentFactory:
    def __init__(
        self, workflow: Any, network: str, langfuse_handler: Any | None = None
    ) -> None:
        self._workflow = workflow
        self._network = network
        self._langfuse_handler = langfuse_handler

    @classmethod
    def from_settings(
        cls, settings: Settings, langfuse_handler: Any | None = None
    ) -> "ContentFactory":
        settings.validate()

        llm = create_llm(settings.llm)
        agents = build_agents(llm, settings.network)
        workflow = build_graph(agents, settings.max_revisions)

        logger.info(
            "Конвейер собран: %s; лимит доработок — %s",
            " → ".join(agents),
            settings.max_revisions,
        )
        return cls(workflow, settings.network, langfuse_handler)

    def run(self, brief: str) -> RunResult:
        config: dict[str, Any] = {}
        if self._langfuse_handler is not None:
            config = {
                "run_name": RUN_NAME,
                "callbacks": [self._langfuse_handler],
                "metadata": {
                    "langfuse_session_id": new_session_id("brief"),
                    "langfuse_tags": [RUN_NAME, f"network:{self._network}"],
                },
            }

        state = self._workflow.invoke(initial_state(brief), config=config)

        return RunResult(
            messages=list(state["messages"]),
            runs=dict(state.get("runs", {})),
            network=self._network,
        )
