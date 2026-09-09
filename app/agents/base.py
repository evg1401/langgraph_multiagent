from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage

if TYPE_CHECKING:  # только для аннотаций
    from app.graph.state import State

logger = logging.getLogger(__name__)

# переключатель внутренних рассуждений модели
THINKING_ON = {"thinking": {"type": "enabled"}}
THINKING_OFF = {"thinking": {"type": "disabled"}}


@dataclass(frozen=True)
class AgentSpec:
    name: str
    persona: str
    temperature: float
    thinking: bool = False
    reasoning_effort: str | None = None

    def model_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {
            "temperature": self.temperature,
            "extra_body": THINKING_ON if self.thinking else THINKING_OFF,
        }
        if self.reasoning_effort is not None:
            params["reasoning_effort"] = self.reasoning_effort

        return params


class LLMAgent:
    def __init__(self, llm: BaseChatModel, spec: AgentSpec) -> None:
        self.spec = spec
        self._model = llm.bind(**spec.model_params())

    @property
    def name(self) -> str:
        return self.spec.name

    def __call__(self, state: "State") -> dict[str, Any]:
        logger.info("[%s] думает…", self.name)

        response = self._model.invoke(
            [SystemMessage(content=self.spec.persona), *state["messages"]]
        )
        response.name = self.name

        # счётчик запусков ведётся одинаково для всех ролей (см. State.runs)
        return {"messages": [response], "runs": {self.name: 1}}
