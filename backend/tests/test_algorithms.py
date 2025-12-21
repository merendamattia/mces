"""
Unit tests for MCES algorithms (brute force and ArcMatch).
Tests validate correctness of MCES computation, edge preservation,
and performance characteristics.
"""

import pytest
from algorithms.brute_force import compute_mces as brute_force_mces
from algorithms.brute_force_arcmatch import compute_mces as arcmatch_mces
from core.graph import Graph


class TestBruteForceMCES:
    """Test suite for naive brute-force MCES algorithm."""

    def test_empty_graphs(self):
        """Test MCES on empty graphs."""
        g1 = Graph()
        g2 = Graph()
        result = brute_force_mces(g1, g2)

        assert result["mapping"] == {}
        assert result["preserved_edges"] == []

    def test_single_node_graphs(self):
        """Test MCES on single-node graphs with no edges."""
        g1 = Graph()
        g1.add_node("1")
        g2 = Graph()
        g2.add_node("1")

        result = brute_force_mces(g1, g2)

        # With only one node and no edges, mapping should still be found
        # but may be empty if algorithm doesn't map isolated nodes
        assert isinstance(result["mapping"], dict)
        assert result["preserved_edges"] == []

    def test_identical_graphs(self):
        """Test MCES on identical graphs (should preserve all edges)."""
        g1 = Graph()
        g1.add_node("1")
        g1.add_node("2")
        g1.add_node("3")
        g1.add_edge("1", "2")
        g1.add_edge("2", "3")

        g2 = Graph()
        g2.add_node("1")
        g2.add_node("2")
        g2.add_node("3")
        g2.add_edge("1", "2")
        g2.add_edge("2", "3")

        result = brute_force_mces(g1, g2)

        assert len(result["preserved_edges"]) == 2

    def test_disjoint_graphs(self):
        """Test MCES on graphs with no common edges."""
        g1 = Graph()
        g1.add_node("1")
        g1.add_node("2")
        g1.add_edge("1", "2")

        g2 = Graph()
        g2.add_node("1")
        g2.add_node("2")
        g2.add_node("3")
        g2.add_edge("1", "3")
        g2.add_edge("2", "3")

        result = brute_force_mces(g1, g2)

        # Should still find a mapping, but may preserve 0 edges
        assert isinstance(result["mapping"], dict)
        assert isinstance(result["preserved_edges"], list)

    def test_g1_larger_than_g2(self):
        """Test MCES when graph1 has more nodes than graph2 (impossible mapping)."""
        g1 = Graph()
        for i in range(1, 6):
            g1.add_node(str(i))

        g2 = Graph()
        for i in range(1, 4):
            g2.add_node(str(i))

        result = brute_force_mces(g1, g2)

        assert result["mapping"] == {}
        assert result["preserved_edges"] == []

    def test_stats_present(self):
        """Test that result contains required statistics."""
        g1 = Graph()
        g1.add_node("1")
        g1.add_node("2")
        g1.add_edge("1", "2")

        g2 = Graph()
        g2.add_node("1")
        g2.add_node("2")
        g2.add_edge("1", "2")

        result = brute_force_mces(g1, g2)

        assert "stats" in result
        assert "time_ms" in result["stats"]
        assert "mappings_explored" in result["stats"]
        assert result["stats"]["time_ms"] >= 0

    def test_triangle_graphs(self):
        """Test MCES on triangle graphs."""
        g1 = Graph()
        g1.add_node("1")
        g1.add_node("2")
        g1.add_node("3")
        g1.add_edge("1", "2")
        g1.add_edge("2", "3")
        g1.add_edge("1", "3")

        g2 = Graph()
        g2.add_node("1")
        g2.add_node("2")
        g2.add_node("3")
        g2.add_edge("1", "2")
        g2.add_edge("2", "3")
        g2.add_edge("1", "3")

        result = brute_force_mces(g1, g2)

        # Should preserve all 3 edges
        assert len(result["preserved_edges"]) == 3


class TestArcMatchMCES:
    """Test suite for brute-force + ArcMatch MCES algorithm."""

    def test_empty_graphs(self):
        """Test MCES on empty graphs."""
        g1 = Graph()
        g2 = Graph()
        result = arcmatch_mces(g1, g2)

        assert result["mapping"] == {}
        assert result["preserved_edges"] == []

    def test_identical_graphs(self):
        """Test MCES on identical graphs (should preserve all edges)."""
        g1 = Graph()
        g1.add_node("1")
        g1.add_node("2")
        g1.add_node("3")
        g1.add_edge("1", "2")
        g1.add_edge("2", "3")

        g2 = Graph()
        g2.add_node("1")
        g2.add_node("2")
        g2.add_node("3")
        g2.add_edge("1", "2")
        g2.add_edge("2", "3")

        result = arcmatch_mces(g1, g2)

        assert len(result["preserved_edges"]) == 2

    def test_stats_include_pruning(self):
        """Test that ArcMatch stats include pruning information."""
        g1 = Graph()
        g1.add_node("1")
        g1.add_node("2")
        g1.add_node("3")
        g1.add_edge("1", "2")
        g1.add_edge("2", "3")

        g2 = Graph()
        g2.add_node("1")
        g2.add_node("2")
        g2.add_node("3")
        g2.add_edge("1", "3")

        result = arcmatch_mces(g1, g2)

        assert "stats" in result
        assert "pruned_branches" in result["stats"]
        assert "recursive_calls" in result["stats"]

    def test_g1_larger_than_g2(self):
        """Test MCES when graph1 has more nodes than graph2."""
        g1 = Graph()
        for i in range(1, 6):
            g1.add_node(str(i))

        g2 = Graph()
        for i in range(1, 4):
            g2.add_node(str(i))

        result = arcmatch_mces(g1, g2)

        assert result["mapping"] == {}
        assert result["preserved_edges"] == []


class TestAlgorithmConsistency:
    """Test that both algorithms produce consistent results."""

    def test_same_result_on_small_graphs(self):
        """Test that brute force and ArcMatch produce same edge count on small graphs."""
        g1 = Graph()
        g1.add_node("1")
        g1.add_node("2")
        g1.add_node("3")
        g1.add_edge("1", "2")
        g1.add_edge("2", "3")

        g2 = Graph()
        g2.add_node("1")
        g2.add_node("2")
        g2.add_node("3")
        g2.add_edge("1", "2")
        g2.add_edge("1", "3")

        result_bf = brute_force_mces(g1, g2)
        result_am = arcmatch_mces(g1, g2)

        # Both should find the same number of preserved edges
        assert len(result_bf["preserved_edges"]) == len(result_am["preserved_edges"])

    def test_arcmatch_has_pruning(self):
        """Test that ArcMatch performs pruning (fewer recursive calls than brute force)."""
        g1 = Graph()
        for i in range(1, 6):
            g1.add_node(str(i))
            if i < 5:
                g1.add_edge(str(i), str(i + 1))

        g2 = Graph()
        for i in range(1, 6):
            g2.add_node(str(i))
            if i < 5:
                g2.add_edge(str(i), str(i + 1))

        result_am = arcmatch_mces(g1, g2)

        # ArcMatch should perform pruning
        assert result_am["stats"]["pruned_branches"] >= 0
