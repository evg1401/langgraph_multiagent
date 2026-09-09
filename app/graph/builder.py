from __future__ import annotations

from typing import Any, Callable, Mapping

from langgraph.graph import END, START, StateGraph

from app.agents.catalog import COPYWRITER, EDITOR, PUBLISHER, STRATEGIST
from app.graph.routing import make_editor_router
from app.graph.state import State

Node = Callable[[State], Mapping[str, Any]]


def build_graph(nodes: Mapping[str, Node], max_revisions: int):
    graph = StateGraph(State)

    for name, node in nodes.items():
        graph.add_node(name, node)

    graph.add_edge(START, STRATEGIST)
    graph.add_edge(STRATEGIST, COPYWRITER)
    graph.add_edge(COPYWRITER, EDITOR)

    # развилка графа
    graph.add_conditional_edges(
        EDITOR,
        make_editor_router(max_revisions),
        {COPYWRITER: COPYWRITER, PUBLISHER: PUBLISHER},
    )
    graph.add_edge(PUBLISHER, END)

    return graph.compile()
