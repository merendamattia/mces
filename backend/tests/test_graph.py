"""
Unit tests for Graph class.
Tests basic graph operations including node/edge addition and validation.
"""

from core.graph import Graph


class TestGraphBasics:
    """Test suite for basic Graph operations."""

    def test_empty_graph(self):
        """Test creating an empty graph."""
        g = Graph()
        assert len(g.nodes) == 0
        assert len(g.edges) == 0

    def test_add_single_node(self):
        """Test adding a single node."""
        g = Graph()
        g.add_node("1")
        assert "1" in g.nodes
        assert len(g.nodes) == 1

    def test_add_multiple_nodes(self):
        """Test adding multiple nodes."""
        g = Graph()
        g.add_node("1")
        g.add_node("2")
        g.add_node("3")
        assert len(g.nodes) == 3
        assert "1" in g.nodes
        assert "2" in g.nodes
        assert "3" in g.nodes

    def test_add_duplicate_node(self):
        """Test that adding duplicate node doesn't increase count."""
        g = Graph()
        g.add_node("1")
        g.add_node("1")
        assert len(g.nodes) == 1

    def test_add_edge(self):
        """Test adding an edge between two nodes."""
        g = Graph()
        g.add_node("1")
        g.add_node("2")
        g.add_edge("1", "2")

        assert len(g.edges) == 1
        # Edge should be stored as sorted tuple
        assert ("1", "2") in g.edges

    def test_add_edge_creates_nodes(self):
        """Test that adding edge does NOT automatically create nodes (must be explicit)."""
        g = Graph()
        g.add_edge("1", "2")

        # Nodes are NOT auto-created - must be added explicitly
        assert "1" not in g.nodes
        assert "2" not in g.nodes
        assert len(g.edges) == 1

    def test_add_duplicate_edge(self):
        """Test that adding duplicate edge doesn't increase count."""
        g = Graph()
        g.add_edge("1", "2")
        g.add_edge("1", "2")
        assert len(g.edges) == 1

    def test_edge_normalization(self):
        """Test that edges are normalized (sorted)."""
        g = Graph()
        g.add_edge("2", "1")
        # Should be stored as ("1", "2")
        assert ("1", "2") in g.edges
        assert ("2", "1") not in g.edges

    def test_to_dict(self):
        """Test conversion to dictionary format."""
        g = Graph()
        g.add_node("1")
        g.add_node("2")
        g.add_edge("1", "2")

        d = g.to_dict()

        assert "nodes" in d
        assert "edges" in d
        assert len(d["nodes"]) == 2
        assert len(d["edges"]) == 1

    def test_to_dict_structure(self):
        """Test that to_dict returns correct structure."""
        g = Graph()
        g.add_node("1")
        g.add_node("2")
        g.add_edge("1", "2")

        d = g.to_dict()

        # Nodes should be a list of dictionaries with 'id' key
        assert isinstance(d["nodes"], list)
        assert all(isinstance(n, dict) and "id" in n for n in d["nodes"])

        # Edges should be a list of dictionaries with 'source' and 'target' keys
        assert isinstance(d["edges"], list)
        assert all(
            isinstance(e, dict) and "source" in e and "target" in e for e in d["edges"]
        )


class TestGraphEdgeCases:
    """Test edge cases and error conditions."""

    def test_self_loop(self):
        """Test that self-loops are rejected."""
        g = Graph()
        g.add_node("1")
        g.add_edge("1", "1")

        # Self-loop should be rejected
        assert "1" in g.nodes
        assert len(g.edges) == 0

    def test_large_graph(self):
        """Test graph with many nodes and edges."""
        g = Graph()
        n = 100
        for i in range(n):
            g.add_node(str(i))

        # Add edges in a chain
        for i in range(n - 1):
            g.add_edge(str(i), str(i + 1))

        assert len(g.nodes) == n
        assert len(g.edges) == n - 1
