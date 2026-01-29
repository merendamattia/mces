import math
import random
import time
from typing import Dict, List, Tuple

from core.graph import Graph


def compute_simulated_annealing_mces(
    graph1: Graph,
    graph2: Graph,
    initial_temperature: float = 100.0,
    cooling_rate: float = 0.95,
    max_iterations: int = 1000,
) -> Dict[str, object]:
    """Solve the MCES problem using Simulated Annealing with Iterated Local Search."""
    start = time.time()

    # Initial solution
    current_alignment = generate_random_alignment(graph1, graph2)
    best_alignment = current_alignment.copy()
    current_score = calculate_common_edges(current_alignment, graph1, graph2)
    best_score = current_score

    temperature = initial_temperature

    for iteration in range(max_iterations):
        # Perturbation and local search
        candidate_alignment = perturb_solution(current_alignment)
        candidate_alignment = greedy_local_search(candidate_alignment, graph1, graph2)
        candidate_score = calculate_common_edges(candidate_alignment, graph1, graph2)

        # Acceptance criterion (Metropolis)
        delta = candidate_score - current_score
        if delta >= 0 or random.random() < math.exp(delta / temperature):
            current_alignment = candidate_alignment
            current_score = candidate_score

            if current_score > best_score:
                best_score = current_score
                best_alignment = current_alignment.copy()

        # Cooling schedule
        temperature *= cooling_rate

        # Convergence check
        if temperature < 0.001:
            break

    elapsed_ms = (time.time() - start) * 1000.0

    # Memory usage
    import os

    import psutil

    process = psutil.Process(os.getpid())
    memory_usage_mb = process.memory_info().rss / 1024 / 1024

    return {
        "mapping": best_alignment,
        "preserved_edges": get_preserved_edges(best_alignment, graph1, graph2),
        "stats": {
            "time_ms": elapsed_ms,
            "mces_size": best_score,
            "memory_usage_mb": memory_usage_mb,
        },
    }


def generate_random_alignment(graph1: Graph, graph2: Graph) -> Dict[str, str]:
    """Generate a random initial alignment."""
    alignment = {}
    available_nodes = list(graph2.nodes)
    random.shuffle(available_nodes)
    for node in graph1.nodes:
        if available_nodes:
            alignment[node] = available_nodes.pop()
    return alignment


def calculate_common_edges(
    alignment: Dict[str, str], graph1: Graph, graph2: Graph
) -> int:
    """Calculate the number of common edges for a given alignment."""
    count = 0
    for u, v in graph1.edges:
        if u in alignment and v in alignment:
            if (alignment[u], alignment[v]) in graph2.edges or (
                alignment[v],
                alignment[u],
            ) in graph2.edges:
                count += 1
    return count


def perturb_solution(alignment: Dict[str, str]) -> Dict[str, str]:
    """Apply a small random change to the current alignment."""
    perturbed = alignment.copy()
    if len(perturbed) > 1:
        node1, node2 = random.sample(list(perturbed.keys()), 2)
        perturbed[node1], perturbed[node2] = perturbed[node2], perturbed[node1]
    return perturbed


def greedy_local_search(
    alignment: Dict[str, str], graph1: Graph, graph2: Graph
) -> Dict[str, str]:
    """Perform a greedy local search to improve the alignment."""
    improved = alignment.copy()
    for node in graph1.nodes:
        if node not in improved:
            continue
        best_target = improved[node]
        best_score = calculate_common_edges(improved, graph1, graph2)
        for target in graph2.nodes:
            if target not in improved.values():
                improved[node] = target
                score = calculate_common_edges(improved, graph1, graph2)
                if score > best_score:
                    best_target = target
                    best_score = score
        improved[node] = best_target
    return improved


def get_preserved_edges(
    alignment: Dict[str, str], graph1: Graph, graph2: Graph
) -> List[Tuple[str, str]]:
    """Get the list of preserved edges based on the alignment."""
    preserved_edges = []
    for u, v in graph1.edges:
        if u in alignment and v in alignment:
            if (alignment[u], alignment[v]) in graph2.edges or (
                alignment[v],
                alignment[u],
            ) in graph2.edges:
                preserved_edges.append((u, v))
    return preserved_edges
