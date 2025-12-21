from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Set, Tuple


@dataclass
class Graph:
    """Lightweight undirected graph suitable for JSON serialization."""

    nodes: Set[str] = field(default_factory=set)
    edges: Set[Tuple[str, str]] = field(default_factory=set)

    def add_node(self, node_id: str) -> None:
        self.nodes.add(node_id)

    def add_edge(self, source: str, target: str) -> None:
        if source == target:
            return  # Avoid self-loops
        ordered = tuple(sorted((source, target)))
        self.edges.add(ordered)

    def to_dict(self) -> Dict[str, object]:
        return {
            "nodes": [{"id": node_id} for node_id in sorted(self.nodes, key=int)],
            "edges": [
                {"source": s, "target": t}
                for s, t in sorted(self.edges, key=lambda x: (int(x[0]), int(x[1])))
            ],
        }
