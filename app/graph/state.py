from __future__ import annotations
from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages


def merge_runs(left: dict[str, int] | None, right: dict[str, int] | None) -> dict[str, int]:
    merged = dict(left or {})
    for name, count in (right or {}).items():
        merged[name] = merged.get(name, 0) + count

    return merged


class State(TypedDict):
    messages: Annotated[list, add_messages]
    # сколько раз отработал каждый агент; наполняется самими узлами
    runs: Annotated[dict[str, int], merge_runs]


def initial_state(brief: str) -> State:
    return {"messages": [HumanMessage(content=brief.strip())], "runs": {}}
