import os
import time
import tracemalloc

import psutil
from pulp import LpMaximize, LpProblem, LpVariable, lpSum

# Start tracking memory usage
tracemalloc.start()


def ilp_r2_mces(graph_g, graph_h):
    """
    Solve the Maximum Common Edge Subgraph (MCES) problem using the ILP R2 formulation.

    Args:
        graph_g (networkx.Graph): The first input graph G.
        graph_h (networkx.Graph): The second input graph H.

    Returns:
        dict: A dictionary containing the solution with the mapping of nodes and edges.
    """
    start_time = time.time()

    # Extract nodes and edges from the graphs
    nodes_g = list(graph_g.nodes)
    nodes_h = list(graph_h.nodes)
    edges_g = list(graph_g.edges)
    edges_h = list(graph_h.edges)

    # Create the ILP problem
    problem = LpProblem("MCES_R2", LpMaximize)

    # Define variables
    x = LpVariable.dicts("x", [(u, v) for u in nodes_g for v in nodes_h], cat="Binary")
    z = LpVariable.dicts(
        "z", [(u1, v2) for u1 in nodes_g for v2 in nodes_h], cat="Binary"
    )

    # Objective function: Maximize the number of common edges
    problem += (
        lpSum(z[u1, v2] for u1 in nodes_g for v2 in nodes_h) / 2,
        "Maximize_Common_Edges",
    )

    # Constraint 1: Each node in G maps to at most one node in H
    for u in nodes_g:
        problem += (
            lpSum(x[u, v] for v in nodes_h) <= 1,
            f"Node_Mapping_Constraint_G_{u}",
        )

    # Constraint 2: Each node in H receives at most one node from G
    for v in nodes_h:
        problem += (
            lpSum(x[u, v] for u in nodes_g) <= 1,
            f"Node_Mapping_Constraint_H_{v}",
        )

    # Constraint 3: Topological consistency (neighbors in G to H)
    for u1 in nodes_g:
        for v2 in nodes_h:
            neighbors_g = list(graph_g.neighbors(u1))
            problem += (
                z[u1, v2] <= lpSum(x[u2, v2] for u2 in neighbors_g),
                f"Topology_Constraint_G_{u1}_{v2}",
            )

    # Constraint 4: Topological consistency (neighbors in H to G)
    for u1 in nodes_g:
        for v2 in nodes_h:
            neighbors_h = list(graph_h.neighbors(v2))
            problem += (
                z[u1, v2] <= lpSum(x[u1, v1] for v1 in neighbors_h),
                f"Topology_Constraint_H_{u1}_{v2}",
            )

    # Solve the problem
    problem.solve()

    # Stop tracking memory usage
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    # Stop tracking execution time
    elapsed_ms = (time.time() - start_time) * 1000.0

    # Memory usage
    process = psutil.Process(os.getpid())
    memory_usage_mb = process.memory_info().rss / 1024 / 1024

    # Check if the problem is empty or infeasible
    if (
        len(nodes_g) == 0 or len(nodes_h) == 0 or problem.status != 1
    ):  # 1 indicates an optimal solution was found
        return {
            "mapping": {},
            "preserved_edges": [],
            "stats": {
                "time_ms": elapsed_ms,
                "memory_usage_mb": memory_usage_mb,
                "solution_optimality": False,
            },
        }

    # Extract the solution
    mapping = {}
    edge_mapping = set()

    for u, v in x:
        if x[u, v].varValue == 1:
            mapping[u] = v

    for u1, v2 in z:
        if z[u1, v2].varValue == 1:
            if (u1, v2) in edges_g and (u1, v2) in edges_h:
                edge_mapping.add((u1, v2))

    # Sort the node mapping to ensure consistency
    mapping = {u: v for u, v in sorted(mapping.items())}

    # Extract preserved nodes and edges
    preserved_nodes = set(mapping.keys())
    preserved_edges = [
        (u, v)
        for u, v in edges_g
        if u in mapping and v in mapping and (mapping[u], mapping[v]) in edges_h
    ]

    # Metrics
    mces_size = len(preserved_edges)
    mapping_quality = mces_size / max(1, len(edges_g)) if edges_g else 0.0
    solution_optimality = True

    return {
        "mapping": mapping,
        "preserved_edges": preserved_edges,
        "stats": {
            "time_ms": elapsed_ms,
            "memory_usage_mb": memory_usage_mb,
            "solution_optimality": solution_optimality,
            "mces_size": mces_size,
            "mapping_quality": mapping_quality,
        },
    }
