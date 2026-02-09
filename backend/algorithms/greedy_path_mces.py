from __future__ import annotations

import time
from itertools import islice, permutations
from typing import Dict, List, Tuple

from core.graph import Graph


class PruningStats:
    def __init__(self) -> None:
        self.recursive_calls = 0
        self.pruned_branches = 0
        self.mappings_explored = 0
        self.valid_edge_checks = 0


def compute_mces_greedy_path(
    graph1: Graph, graph2: Graph, max_path_len: int = 4
) -> Dict[str, object]:
    """Greedy path-based heuristic for MCES (standalone implementation).

    Finds short simple paths in graph1 and greedily maps them to available
    targets in graph2 to maximize newly preserved edges.
    """

    start = time.time()

    available_targets = set(graph2.nodes)
    mapping: Dict[str, str] = {}
    preserved_edges: List[Tuple[str, str]] = []

    def enumerate_paths(start_node: str, max_len: int) -> List[List[str]]:
        paths: List[List[str]] = []

        def dfs(path: List[str]):
            if 1 <= len(path) <= max_len:
                paths.append(list(path))
            if len(path) == max_len:
                return
            last = path[-1]
            for u, v in graph1.edges:
                nb = None
                if u == last and v not in path:
                    nb = v
                elif v == last and u not in path:
                    nb = u
                if nb is not None:
                    path.append(nb)
                    dfs(path)
                    path.pop()

        dfs([start_node])
        return paths

    def count_preserved_edges_for_mapping(
        ext_mapping: Dict[str, str]
    ) -> Tuple[int, List[Tuple[str, str]]]:
        new_preserved: List[Tuple[str, str]] = []
        # edges inside newly mapped nodes
        for u, v in graph1.edges:
            if u in ext_mapping and v in ext_mapping:
                if tuple(sorted((ext_mapping[u], ext_mapping[v]))) in graph2.edges:
                    new_preserved.append((u, v))
        # edges between newly mapped nodes and already mapped nodes
        for u, v in graph1.edges:
            if (u in ext_mapping and v in mapping) or (
                v in ext_mapping and u in mapping
            ):
                mu = ext_mapping[u] if u in ext_mapping else mapping[u]
                mv = ext_mapping[v] if v in ext_mapping else mapping[v]
                if tuple(sorted((mu, mv))) in graph2.edges:
                    new_preserved.append((u, v))
        # deduplicate
        new_preserved = list({tuple(sorted(e)): e for e in new_preserved}.values())
        return len(new_preserved), new_preserved

    # Main greedy loop
    while True:
        best_gain = 0
        best_ext: Dict[str, str] = {}
        best_ext_preserved: List[Tuple[str, str]] = []

        remaining_nodes = [n for n in sorted(graph1.nodes, key=int) if n not in mapping]
        if not remaining_nodes:
            break

        for start_node in remaining_nodes:
            paths = enumerate_paths(start_node, max_path_len)
            for path in paths:
                path_nodes = [n for n in path if n not in mapping]
                if not path_nodes:
                    continue
                if len(available_targets) < len(path_nodes):
                    continue

                max_perms = 2000
                perms = permutations(
                    sorted(available_targets, key=int), len(path_nodes)
                )
                for perm in islice(perms, max_perms):
                    ext = {node: tgt for node, tgt in zip(path_nodes, perm)}
                    gain, new_pres = count_preserved_edges_for_mapping(ext)
                    if gain > best_gain:
                        best_gain = gain
                        best_ext = ext
                        best_ext_preserved = new_pres
                if best_gain >= len(path_nodes):
                    break
            if best_gain >= len(start_node):
                break

        if best_gain <= 0:
            break

        # Apply best extension
        for n, t in best_ext.items():
            mapping[n] = t
            if t in available_targets:
                available_targets.remove(t)
        existing_set = {tuple(sorted(e)) for e in preserved_edges}
        for e in best_ext_preserved:
            if tuple(sorted(e)) not in existing_set:
                preserved_edges.append(e)
                existing_set.add(tuple(sorted(e)))

    elapsed_ms = (time.time() - start) * 1000.0
    stats = PruningStats()
    stats.mappings_explored = 0
    stats.recursive_calls = 0

    search_space_size = len(graph1.nodes) * len(graph2.nodes)
    solution_optimality = False  # Greedy heuristic does not guarantee optimality

    import os

    import psutil

    process = psutil.Process(os.getpid())
    memory_usage_mb = process.memory_info().rss / 1024 / 1024

    return {
        "mapping": mapping,
        "preserved_edges": [[u, v] for u, v in preserved_edges],
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
