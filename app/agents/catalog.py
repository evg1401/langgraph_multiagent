from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from app import personas
from app.agents.base import AgentSpec, LLMAgent

# имена узлов графа — единственный источник истины для маршрутизации
STRATEGIST = "strategist"
COPYWRITER = "copywriter"
EDITOR = "editor"
PUBLISHER = "publisher"


def build_specs(network: str) -> tuple[AgentSpec, ...]:
    # описание пайплайна: стратег -> копирайтер -> редактор -> паблишер
    return (
        AgentSpec(
            name=STRATEGIST,
            persona=personas.STRATEGIST,
            temperature=0.4,
            thinking=True,
            reasoning_effort="high",
        ),
        AgentSpec(
            name=COPYWRITER,
            persona=personas.COPYWRITER,
            temperature=0.8,
        ),
        AgentSpec(
            name=EDITOR,
            persona=personas.EDITOR,
            temperature=0.2,
            thinking=True,
            reasoning_effort="medium",
        ),
        AgentSpec(
            name=PUBLISHER,
            persona=personas.publisher(network),
            temperature=0.4,
        ),
    )


def build_agents(llm: BaseChatModel, network: str) -> dict[str, LLMAgent]:
    return {spec.name: LLMAgent(llm, spec) for spec in build_specs(network)}
