from __future__ import annotations

import itertools
import os
import time
from typing import Dict, List, Tuple

import psutil
from core.graph import Graph


def compute_mces(graph1: Graph, graph2: Graph) -> Dict[str, object]:
    """Naïve brute-force MCES via full permutation enumeration.

    Assumes small graphs (<= 8-10 nodes) due to combinatorial explosion.
    """

    start = time.time()

    nodes1 = sorted(graph1.nodes, key=int)
    nodes2 = sorted(graph2.nodes, key=int)

    if len(nodes1) > len(nodes2):
        # No injective mapping possible if graph1 has more nodes.
        return {
            "mapping": {},
            "preserved_edges": [],
            "stats": {
                "time_ms": 0.0,
                "mappings_explored": 0,
                "recursive_calls": 0,
                "pruned_branches": 0,
            },
        }

    best_mapping: Dict[str, str] = {}
    best_preserved_edges: List[Tuple[str, str]] = []
    mappings_explored = 0

    for perm in itertools.permutations(nodes2, len(nodes1)):
        mapping = dict(zip(nodes1, perm))
        mappings_explored += 1

        preserved = []
        for u, v in graph1.edges:
            if u in mapping and v in mapping:
                mu, mv = mapping[u], mapping[v]
                if tuple(sorted((mu, mv))) in graph2.edges:
                    preserved.append((u, v))

        if len(preserved) > len(best_preserved_edges):
            best_mapping = mapping
            best_preserved_edges = preserved

    elapsed_ms = (time.time() - start) * 1000.0

    process = psutil.Process(os.getpid())
    memory_usage_mb = process.memory_info().rss / 1024 / 1024

    search_space_size = len(nodes1) * len(nodes2)

    solution_optimality = True  # Brute-force guarantees optimality

    return {
        "mapping": best_mapping,
        "preserved_edges": [[u, v] for u, v in best_preserved_edges],
        "stats": {
            "time_ms": elapsed_ms,
            "mappings_explored": mappings_explored,
            "recursive_calls": 0,
            "pruned_branches": 0,
            "search_space_size": search_space_size,
            "memory_usage_mb": memory_usage_mb,
            "solution_optimality": solution_optimality,
        },
    }
