from __future__ import annotations

import itertools
import math
import random
from typing import Tuple

from core.graph import Graph


def generate_random_graph(num_nodes: int, num_edges: int) -> Graph:
    """Generate a connected undirected graph with up to num_edges edges.

    Guarantees the graph is connected by first creating a spanning tree,
    then adding additional edges randomly. For n nodes, the minimum number
    of edges is (n-1) to ensure connectivity.
    """

    graph = Graph()
    node_ids = [str(i + 1) for i in range(num_nodes)]
    for node_id in node_ids:
        graph.add_node(node_id)

    if num_nodes <= 1:
        return graph

    possible_edges = list(itertools.combinations(node_ids, 2))
    max_edges = len(possible_edges)

    # For a connected graph we need at least (n-1) edges
    min_required = num_nodes - 1
    target_edges = max(min(num_edges, max_edges), min_required)

    # Step 1: Create a spanning tree to ensure connectivity
    # Shuffle nodes and connect them in sequence
    shuffled = node_ids[:]
    random.shuffle(shuffled)

    spanning_tree_edges = []
    for i in range(len(shuffled) - 1):
        u = shuffled[i]
        v = shuffled[i + 1]
        spanning_tree_edges.append(tuple(sorted((u, v))))

    # Add spanning tree edges to graph
    for source, target in spanning_tree_edges:
        graph.add_edge(source, target)

    # Step 2: Add remaining edges randomly
    remaining_needed = target_edges - len(graph.edges)
    if remaining_needed > 0:
        existing = set(graph.edges)
        available_edges = [e for e in possible_edges if e not in existing]
        if len(available_edges) > 0:
            sampled_count = min(remaining_needed, len(available_edges))
            sampled_edges = random.sample(available_edges, sampled_count)
            for source, target in sampled_edges:
                graph.add_edge(source, target)

    return graph


def generate_random_graph_pair(num_nodes: int, num_edges: int) -> Tuple[Graph, Graph]:
    """Generate two independent random graphs with the same parameters."""

    g1 = generate_random_graph(num_nodes=num_nodes, num_edges=num_edges)
    g2 = generate_random_graph(num_nodes=num_nodes, num_edges=num_edges)
    return g1, g2
