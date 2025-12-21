from __future__ import annotations

from core.generator import generate_random_graph_pair
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
