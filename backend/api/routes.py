from __future__ import annotations

from algorithms import (
    compute_mces_bruteforce,
    compute_mces_bruteforce_arcmatch,
    compute_mces_connected,
    compute_mces_greedy_path,
    compute_mces_simulated_annealing,
)
from algorithms.ilp_r2 import compute_mces_ilp_r2
from core.generator import generate_random_graph_pair
from core.graph import Graph
from flask import Blueprint, jsonify, request

api_bp = Blueprint("api", __name__)


@api_bp.route("/generate", methods=["POST"])
def generate_graphs():
    """Generate two random graphs based on the provided parameters."""
    payload = request.get_json(silent=True) or {}
    try:
        num_nodes = int(payload.get("num_nodes", 0))
        num_edges = int(payload.get("num_edges", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "num_nodes and num_edges must be integers"}), 400

    if num_nodes <= 0:
        return jsonify({"error": "num_nodes must be positive"}), 400
    if num_edges < 0:
        return jsonify({"error": "num_edges cannot be negative"}), 400

    graph1, graph2 = generate_random_graph_pair(
        num_nodes=num_nodes, num_edges=num_edges
    )

    return jsonify({"graph1": graph1.to_dict(), "graph2": graph2.to_dict()})


def _graph_from_dict(data: dict) -> Graph:
    graph = Graph()
    for node in data.get("nodes", []):
        graph.add_node(str(node.get("id")))
    for edge in data.get("edges", []):
        s = str(edge.get("source"))
        t = str(edge.get("target"))
        graph.add_edge(s, t)
    return graph


def _parse_graphs_payload(payload: dict):
    g1_raw = payload.get("graph1")
    g2_raw = payload.get("graph2")
    if not g1_raw or not g2_raw:
        return None, None, jsonify({"error": "graph1 and graph2 are required"}), 400
    try:
        g1 = _graph_from_dict(g1_raw)
        g2 = _graph_from_dict(g2_raw)
        return g1, g2, None, None
    except Exception:
        return None, None, jsonify({"error": "invalid graph format"}), 400


@api_bp.route("/mces/bruteforce", methods=["POST"])
def run_bruteforce():
    payload = request.get_json(silent=True) or {}
    g1, g2, err_resp, status = _parse_graphs_payload(payload)
    if err_resp:
        return err_resp, status
    result = compute_mces_bruteforce(g1, g2)
    return jsonify({"algorithm": "bruteforce", "result": result})


@api_bp.route("/mces/bruteforce_arcmatch", methods=["POST"])
def run_bruteforce_arcmatch():
    payload = request.get_json(silent=True) or {}
    g1, g2, err_resp, status = _parse_graphs_payload(payload)
    if err_resp:
        return err_resp, status
    result = compute_mces_bruteforce_arcmatch(g1, g2)
    return jsonify({"algorithm": "bruteforce_arcmatch", "result": result})


@api_bp.route("/mces/connected", methods=["POST"])
def run_connected_mces():
    payload = request.get_json(silent=True) or {}
    g1, g2, err_resp, status = _parse_graphs_payload(payload)
    if err_resp:
        return err_resp, status
    result = compute_mces_connected(g1, g2)
    return jsonify({"algorithm": "connected_mces", "result": result})


@api_bp.route("/mces/greedy_path", methods=["POST"])
def run_greedy_path_mces():
    payload = request.get_json(silent=True) or {}
    g1, g2, err_resp, status = _parse_graphs_payload(payload)
    if err_resp:
        return err_resp, status
    # allow optional path length parameter
    max_len = None
    try:
        max_len = int((payload or {}).get("max_path_len", 4))
    except (TypeError, ValueError):
        max_len = 4
    result = compute_mces_greedy_path(g1, g2)
    return jsonify({"algorithm": "greedy_path_mces", "result": result})


@api_bp.route("/mces/ilp_r2", methods=["POST"])
def run_compute_mces_ilp_r2():
    payload = request.get_json(silent=True) or {}
    g1, g2, err_resp, status = _parse_graphs_payload(payload)
    if err_resp:
        return err_resp, status
    result = compute_mces_ilp_r2(g1, g2)

    # Extract preserved nodes and edges for response
    preserved_nodes = result.get("preserved_nodes", [])
    preserved_edges = result.get("preserved_edges", [])

    return jsonify(
        {
            "algorithm": "ilp_r2",
            "result": result,
            "preserved_nodes": preserved_nodes,
            "preserved_edges": preserved_edges,
        }
    )


@api_bp.route("/mces/simulated_annealing", methods=["POST"])
def run_simulated_annealing():
    payload = request.get_json(silent=True) or {}
    g1, g2, err_resp, status = _parse_graphs_payload(payload)
    if err_resp:
        return err_resp, status

    initial_temperature = payload.get("initial_temperature", 100.0)
    cooling_rate = payload.get("cooling_rate", 0.95)
    max_iterations = payload.get("max_iterations", 1000)

    result = compute_mces_simulated_annealing(
        g1,
        g2,
        initial_temperature=initial_temperature,
        cooling_rate=cooling_rate,
        max_iterations=max_iterations,
    )
    return jsonify({"algorithm": "simulated_annealing", "result": result})
