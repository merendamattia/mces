from __future__ import annotations

import itertools
import time
from typing import Dict, List, Tuple

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
            mu, mv = mapping[u], mapping[v]
            if tuple(sorted((mu, mv))) in graph2.edges:
                preserved.append((u, v))

        if len(preserved) > len(best_preserved_edges):
            best_mapping = mapping
            best_preserved_edges = preserved

    elapsed_ms = (time.time() - start) * 1000.0

    # Metrics
    mces_size = len(best_preserved_edges)
    mapping_quality = mces_size / max(1, len(graph1.edges)) if graph1.edges else 0.0
    solution_optimality = True  # brute-force is optimal
    # Memory usage placeholder (can be replaced with actual measurement)
    import os

    import psutil

    process = psutil.Process(os.getpid())
    memory_usage_mb = process.memory_info().rss / 1024 / 1024

    return {
        "mapping": best_mapping,
        "preserved_edges": [[u, v] for u, v in best_preserved_edges],
        "stats": {
            "time_ms": elapsed_ms,
            "mappings_explored": mappings_explored,
            "recursive_calls": 0,
            "pruned_branches": 0,
            "mces_size": mces_size,
            "mapping_quality": mapping_quality,
            "solution_optimality": solution_optimality,
            "memory_usage_mb": memory_usage_mb,
        },
    }


# Extension point: future variants (e.g., heuristic ordering) can branch from here.
