from __future__ import annotations

import time
from typing import Dict, List, Tuple

from core.graph import Graph


class PruningStats:
    def __init__(self) -> None:
        self.recursive_calls = 0
        self.pruned_branches = 0
        self.mappings_explored = 0


def _preserved_edges(
    graph1: Graph, graph2: Graph, mapping: Dict[str, str], stats: PruningStats
) -> List[Tuple[str, str]]:
    preserved: List[Tuple[str, str]] = []
    for u, v in graph1.edges:
        if u in mapping and v in mapping:
            mu, mv = mapping[u], mapping[v]
            if tuple(sorted((mu, mv))) in graph2.edges:
                preserved.append((u, v))
    return preserved


def _can_potentially_improve(
    graph1: Graph,
    graph2: Graph,
    current_mapping: Dict[str, str],
    used_targets: set,
    current_index: int,
    total_nodes: int,
    best_preserved_count: int,
    stats: PruningStats,
) -> bool:
    already_preserved = 0
    potentially_preservable = 0

    mapped_nodes = set(current_mapping.keys())

    for u, v in graph1.edges:
        u_mapped = u in mapped_nodes
        v_mapped = v in mapped_nodes

        if u_mapped and v_mapped:
            mu, mv = current_mapping[u], current_mapping[v]
            if tuple(sorted((mu, mv))) in graph2.edges:
                already_preserved += 1
        else:
            potentially_preservable += 1

    return (already_preserved + potentially_preservable) > best_preserved_count


def _result(
    best_mapping: Dict[str, str],
    best_preserved_edges: List[Tuple[str, str]],
    stats: PruningStats,
    elapsed_ms: float,
    graph1: Graph,
    graph2: Graph,
) -> Dict[str, object]:
    search_space_size = len(graph1.nodes) * len(graph2.nodes)

    solution_optimality = True

    import os

    import psutil

    process = psutil.Process(os.getpid())
    memory_usage_mb = process.memory_info().rss / 1024 / 1024
    return {
        "mapping": best_mapping,
        "preserved_edges": [[u, v] for u, v in best_preserved_edges],
        "stats": {
            "time_ms": elapsed_ms,
            "mappings_explored": stats.mappings_explored,
            "recursive_calls": stats.recursive_calls,
            "pruned_branches": stats.pruned_branches,
            "search_space_size": search_space_size,
            "memory_usage_mb": memory_usage_mb,
            "solution_optimality": solution_optimality,
        },
    }


def compute_mces_connected(graph1: Graph, graph2: Graph) -> Dict[str, object]:
    """Backtracking MCES that requires the preserved subgraph of graph1 to be connected.

    Uses pruning and returns only mappings whose preserved edges
    in graph1 induce a single connected component.
    """

    start = time.time()

    nodes1 = sorted(graph1.nodes, key=int)
    nodes2 = sorted(graph2.nodes, key=int)

    best_mapping: Dict[str, str] = {}
    best_preserved_edges: List[Tuple[str, str]] = []
    stats = PruningStats()

    if len(nodes1) > len(nodes2):
        elapsed_ms = (time.time() - start) * 1000.0
        return _result(
            best_mapping, best_preserved_edges, stats, elapsed_ms, graph1, graph2
        )

    used_targets = set()
    current_mapping: Dict[str, str] = {}

    def _is_preserved_connected(preserved: List[Tuple[str, str]]) -> bool:
        if not preserved:
            return False
        adj: Dict[str, List[str]] = {}
        for u, v in preserved:
            adj.setdefault(u, []).append(v)
            adj.setdefault(v, []).append(u)
        start_node = preserved[0][0]
        seen = {start_node}
        stack = [start_node]
        while stack:
            n = stack.pop()
            for nb in adj.get(n, []):
                if nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
        nodes_in_preserved = {n for e in preserved for n in e}
        return seen >= nodes_in_preserved

    def backtrack(index: int) -> None:
        stats.recursive_calls += 1

        if index == len(nodes1):
            stats.mappings_explored += 1
            preserved = _preserved_edges(graph1, graph2, current_mapping, stats)
            nonlocal best_mapping, best_preserved_edges
            if _is_preserved_connected(preserved) and len(preserved) >= len(
                best_preserved_edges
            ):
                best_mapping = dict(current_mapping)
                best_preserved_edges = preserved
            return

        node = nodes1[index]
        for target in nodes2:
            if target in used_targets:
                continue
            current_mapping[node] = target
            used_targets.add(target)

            can_improve = _can_potentially_improve(
                graph1,
                graph2,
                current_mapping,
                used_targets,
                index,
                len(nodes1),
                len(best_preserved_edges),
                stats,
            )

            if can_improve:
                backtrack(index + 1)
            else:
                stats.pruned_branches += 1

            used_targets.remove(target)
            current_mapping.pop(node, None)

    backtrack(0)

    elapsed_ms = (time.time() - start) * 1000.0
    return _result(
        best_mapping, best_preserved_edges, stats, elapsed_ms, graph1, graph2
    )
