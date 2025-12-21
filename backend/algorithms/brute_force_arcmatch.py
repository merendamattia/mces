from __future__ import annotations

import time
from typing import Dict, List, Tuple

from core.graph import Graph


class ArcMatchStats:
    def __init__(self) -> None:
        self.recursive_calls = 0
        self.pruned_branches = 0
        self.mappings_explored = 0
        self.valid_edge_checks = 0


def compute_mces(graph1: Graph, graph2: Graph) -> Dict[str, object]:
    """Brute-force MCES with ArcMatch pruning via backtracking.

    Suitable for small graphs (<= 8-10 nodes). Applies injectivity and
    endpoint-consistency checks during search to prune early.
    """

    start = time.time()

    nodes1 = sorted(graph1.nodes, key=int)
    nodes2 = sorted(graph2.nodes, key=int)

    best_mapping: Dict[str, str] = {}
    best_preserved_edges: List[Tuple[str, str]] = []
    stats = ArcMatchStats()

    if len(nodes1) > len(nodes2):
        elapsed_ms = (time.time() - start) * 1000.0
        return _result(best_mapping, best_preserved_edges, stats, elapsed_ms)

    used_targets = set()
    current_mapping: Dict[str, str] = {}

    def backtrack(index: int) -> None:
        stats.recursive_calls += 1

        if index == len(nodes1):
            stats.mappings_explored += 1
            preserved = _preserved_edges(graph1, graph2, current_mapping, stats)
            nonlocal best_mapping, best_preserved_edges
            if len(preserved) >= len(best_preserved_edges):
                best_mapping = dict(current_mapping)
                best_preserved_edges = preserved
            return

        node = nodes1[index]
        for target in nodes2:
            if target in used_targets:
                continue
            current_mapping[node] = target
            used_targets.add(target)

            # ArcMatch pruning: check if we can still beat the best solution
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
    return _result(best_mapping, best_preserved_edges, stats, elapsed_ms)


# Helpers


def _preserved_edges(
    graph1: Graph, graph2: Graph, mapping: Dict[str, str], stats: ArcMatchStats
) -> List[Tuple[str, str]]:
    preserved: List[Tuple[str, str]] = []
    for u, v in graph1.edges:
        stats.valid_edge_checks += 1
        if u in mapping and v in mapping:
            mu, mv = mapping[u], mapping[v]
            if tuple(sorted((mu, mv))) in graph2.edges:
                preserved.append((u, v))
    return preserved


def _is_partial_mapping_consistent(
    graph1: Graph, graph2: Graph, mapping: Dict[str, str], stats: ArcMatchStats
) -> bool:
    # ArcMatch rules:
    # 1) If both endpoints are mapped, the corresponding edge must exist in graph2.
    # 2) Injectivity is handled by caller via used_targets set.

    for u, v in graph1.edges:
        u_mapped = u in mapping
        v_mapped = v in mapping

        if u_mapped and v_mapped:
            stats.valid_edge_checks += 1
            mu, mv = mapping[u], mapping[v]
            if tuple(sorted((mu, mv))) not in graph2.edges:
                return False  # endpoint consistency failed

    return True


def _can_potentially_improve(
    graph1: Graph,
    graph2: Graph,
    current_mapping: Dict[str, str],
    used_targets: set,
    current_index: int,
    total_nodes: int,
    best_preserved_count: int,
    stats: ArcMatchStats,
) -> bool:
    """Check if current partial mapping can potentially beat the best solution.

    Computes:
    - already_preserved: edges with both endpoints already mapped and preserved
    - potentially_preservable: edges with at least one unmapped endpoint

    If already_preserved + potentially_preservable <= best_preserved_count,
    we can prune this branch.
    """
    already_preserved = 0
    potentially_preservable = 0

    mapped_nodes = set(current_mapping.keys())

    for u, v in graph1.edges:
        u_mapped = u in mapped_nodes
        v_mapped = v in mapped_nodes

        if u_mapped and v_mapped:
            # Check if this edge is preserved
            stats.valid_edge_checks += 1
            mu, mv = current_mapping[u], current_mapping[v]
            if tuple(sorted((mu, mv))) in graph2.edges:
                already_preserved += 1
        else:
            # At least one endpoint not yet mapped - might be preservable
            potentially_preservable += 1

    # If even with all potential edges we can't beat best, prune
    return (already_preserved + potentially_preservable) > best_preserved_count


def _result(
    best_mapping: Dict[str, str],
    best_preserved_edges: List[Tuple[str, str]],
    stats: ArcMatchStats,
    elapsed_ms: float,
) -> Dict[str, object]:
    return {
        "mapping": best_mapping,
        "preserved_edges": [[u, v] for u, v in best_preserved_edges],
        "stats": {
            "time_ms": elapsed_ms,
            "mappings_explored": stats.mappings_explored,
            "recursive_calls": stats.recursive_calls,
            "pruned_branches": stats.pruned_branches,
            "valid_edge_checks": stats.valid_edge_checks,
        },
    }


# Extension point: additional pruning heuristics (e.g., degree ordering) can be layered here.
