"""
Unit tests for graph generation functionality.
Tests ensure graphs are connected, have correct number of nodes/edges,
and adhere to structural constraints.
"""

import pytest
from core.generator import generate_random_graph, generate_random_graph_pair
from core.graph import Graph


class TestGenerateRandomGraph:
    """Test suite for generate_random_graph function."""

    def test_empty_graph(self):
        """Test generation of empty graph with 0 nodes."""
        graph = generate_random_graph(0, 0)
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_single_node(self):
        """Test generation of single node graph."""
        graph = generate_random_graph(1, 0)
        assert len(graph.nodes) == 1
        assert len(graph.edges) == 0

    def test_minimal_connected_graph(self):
        """Test generation of minimal connected graph (n nodes, n-1 edges)."""
        num_nodes = 5
        graph = generate_random_graph(num_nodes, num_nodes - 1)
        assert len(graph.nodes) == num_nodes
        assert len(graph.edges) == num_nodes - 1
        assert self._is_connected(graph)

    def test_connectivity_guaranteed(self):
        """Test that generated graphs are always connected."""
        for num_nodes in [3, 5, 8, 10]:
            for num_edges in range(num_nodes - 1, num_nodes * (num_nodes - 1) // 2 + 1):
                graph = generate_random_graph(num_nodes, num_edges)
                assert self._is_connected(
                    graph
                ), f"Graph with {num_nodes} nodes and {num_edges} edges is not connected"

    def test_edge_count_respects_limits(self):
        """Test that edge count doesn't exceed maximum possible edges."""
        num_nodes = 6
        max_edges = num_nodes * (num_nodes - 1) // 2

        # Request more edges than possible
        graph = generate_random_graph(num_nodes, max_edges + 10)
        assert len(graph.edges) <= max_edges

    def test_minimum_edges_enforced(self):
        """Test that minimum edges (n-1) are enforced for connectivity."""
        num_nodes = 7
        # Request fewer edges than needed for connectivity
        graph = generate_random_graph(num_nodes, 2)
        assert len(graph.edges) >= num_nodes - 1

    def test_node_ids_sequential(self):
        """Test that nodes have sequential IDs starting from 1."""
        num_nodes = 5
        graph = generate_random_graph(num_nodes, 4)
        expected_ids = {str(i + 1) for i in range(num_nodes)}
        assert set(graph.nodes) == expected_ids

    def test_no_self_loops(self):
        """Test that graph doesn't contain self-loops."""
        graph = generate_random_graph(10, 15)
        for source, target in graph.edges:
            assert source != target

    def test_no_duplicate_edges(self):
        """Test that graph doesn't contain duplicate edges."""
        graph = generate_random_graph(10, 20)
        edges_set = set(graph.edges)
        assert len(edges_set) == len(graph.edges)

    def test_edges_normalized(self):
        """Test that edges are stored in normalized form (sorted tuples)."""
        graph = generate_random_graph(8, 12)
        for source, target in graph.edges:
            assert source <= target, "Edges should be stored as (min, max) tuples"

    @staticmethod
    def _is_connected(graph: Graph) -> bool:
        """Check if graph is connected using BFS."""
        if len(graph.nodes) == 0:
            return True

        if len(graph.nodes) == 1:
            return True

        # Build adjacency list
        adj = {node: set() for node in graph.nodes}
        for source, target in graph.edges:
            adj[source].add(target)
            adj[target].add(source)

        # BFS from first node
        start_node = next(iter(graph.nodes))
        visited = {start_node}
        queue = [start_node]

        while queue:
            node = queue.pop(0)
            for neighbor in adj[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return len(visited) == len(graph.nodes)


class TestGenerateRandomGraphPair:
    """Test suite for generate_random_graph_pair function."""

    def test_generates_two_graphs(self):
        """Test that function generates exactly two graphs."""
        g1, g2 = generate_random_graph_pair(5, 6)
        assert isinstance(g1, Graph)
        assert isinstance(g2, Graph)

    def test_graphs_are_independent(self):
        """Test that generated graphs are different instances."""
        g1, g2 = generate_random_graph_pair(6, 8)
        assert g1 is not g2
        # Graphs should generally be different (not always, but very likely)
        # Check they don't share the same edge set
        assert g1.edges is not g2.edges

    def test_both_graphs_have_same_parameters(self):
        """Test that both graphs have same number of nodes."""
        num_nodes = 7
        g1, g2 = generate_random_graph_pair(num_nodes, 10)
        assert len(g1.nodes) == num_nodes
        assert len(g2.nodes) == num_nodes

    def test_both_graphs_are_connected(self):
        """Test that both graphs in pair are connected."""
        g1, g2 = generate_random_graph_pair(8, 12)
        assert TestGenerateRandomGraph._is_connected(g1)
        assert TestGenerateRandomGraph._is_connected(g2)
