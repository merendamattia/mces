from __future__ import annotations

from algorithms import compute_mces_bruteforce, compute_mces_bruteforce_arcmatch
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
