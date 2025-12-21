from __future__ import annotations

import itertools
import math
import random
from typing import Tuple

from core.graph import Graph


def generate_random_graph(num_nodes: int, num_edges: int) -> Graph:
    """Generate an undirected graph with up to num_edges edges.

    Guarantees every node has degree >= 1 when num_nodes > 1 by first creating
    a minimal pairing, then sampling the remaining edges without replacement.
    The requested edge count is clipped to respect graph constraints and the
    degree guarantee.
    """

    graph = Graph()
    node_ids = [str(i + 1) for i in range(num_nodes)]
    for node_id in node_ids:
        graph.add_node(node_id)

    if num_nodes <= 1:
        return graph

    possible_edges = list(itertools.combinations(node_ids, 2))
    max_edges = len(possible_edges)
    min_required = math.ceil(
        num_nodes / 2
    )  # minimal edges so each node has degree >= 1
    target_edges = max(min(num_edges, max_edges), min_required)

    # Ensure each node has at least one edge via random pairing (wrap last if odd).
    shuffled = node_ids[:]
    random.shuffle(shuffled)
    initial_edges = []
    for i in range(0, len(shuffled), 2):
        u = shuffled[i]
        v = shuffled[(i + 1) % len(shuffled)]
        if u != v:
            initial_edges.append(tuple(sorted((u, v))))

    for source, target in initial_edges:
        graph.add_edge(source, target)

    remaining_needed = target_edges - len(graph.edges)
    if remaining_needed > 0:
        existing = set(graph.edges)
        available_edges = [e for e in possible_edges if e not in existing]
        sampled_edges = random.sample(available_edges, remaining_needed)
        for source, target in sampled_edges:
            graph.add_edge(source, target)

    return graph


def generate_random_graph_pair(num_nodes: int, num_edges: int) -> Tuple[Graph, Graph]:
    """Generate two independent random graphs with the same parameters."""

    g1 = generate_random_graph(num_nodes=num_nodes, num_edges=num_edges)
    g2 = generate_random_graph(num_nodes=num_nodes, num_edges=num_edges)
    return g1, g2
