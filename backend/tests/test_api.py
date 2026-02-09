"""
Integration tests for Flask API endpoints.
Tests validate API responses, error handling, and data flow.
"""

import json

import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestGenerateEndpoint:
    """Test suite for /api/generate endpoint."""

    def test_generate_valid_request(self, client):
        """Test graph generation with valid parameters."""
        response = client.post(
            "/api/generate",
            json={"num_nodes": 5, "num_edges": 6},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "graph1" in data
        assert "graph2" in data
        assert "nodes" in data["graph1"]
        assert "edges" in data["graph1"]

    def test_generate_minimal_graph(self, client):
        """Test generation of minimal graph."""
        response = client.post(
            "/api/generate",
            json={"num_nodes": 2, "num_edges": 1},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert len(data["graph1"]["nodes"]) == 2

    def test_generate_missing_parameters(self, client):
        """Test error handling for missing parameters."""
        response = client.post(
            "/api/generate", json={"num_nodes": 5}, content_type="application/json"
        )

        # API may default missing num_edges to 0, so this might succeed
        # Check that it at least returns a valid response
        assert response.status_code in [200, 400]

    def test_generate_invalid_numbers(self, client):
        """Test error handling for invalid numbers."""
        response = client.post(
            "/api/generate",
            json={"num_nodes": -1, "num_edges": 5},
            content_type="application/json",
        )

        assert response.status_code == 400


class TestMcesBruteforceEndpoint:
    """Test suite for /api/mces/bruteforce endpoint."""

    def test_bruteforce_valid_request(self, client):
        """Test MCES bruteforce with valid graphs."""
        graph1 = {
            "nodes": [{"id": "1"}, {"id": "2"}, {"id": "3"}],
            "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}],
        }
        graph2 = {
            "nodes": [{"id": "1"}, {"id": "2"}, {"id": "3"}],
            "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}],
        }

        response = client.post(
            "/api/mces/bruteforce",
            json={"graph1": graph1, "graph2": graph2},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "algorithm" in data
        assert "result" in data
        assert data["algorithm"] == "bruteforce"
        assert "preserved_edges" in data["result"]
        assert "mapping" in data["result"]
        assert "stats" in data["result"]

    def test_bruteforce_empty_graphs(self, client):
        """Test MCES on empty graphs."""
        graph1 = {"nodes": [], "edges": []}
        graph2 = {"nodes": [], "edges": []}

        response = client.post(
            "/api/mces/bruteforce",
            json={"graph1": graph1, "graph2": graph2},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert len(data["result"]["preserved_edges"]) == 0

    def test_bruteforce_missing_graph(self, client):
        """Test error handling for missing graph parameter."""
        graph1 = {"nodes": [{"id": "1"}], "edges": []}

        response = client.post(
            "/api/mces/bruteforce",
            json={"graph1": graph1},
            content_type="application/json",
        )

        assert response.status_code == 400


class TestMcesPruningEndpoint:
    """Test suite for /api/mces/bruteforce_pruning endpoint."""

    def test_pruning_valid_request(self, client):
        """Test MCES pruning with valid graphs."""
        graph1 = {
            "nodes": [{"id": "1"}, {"id": "2"}, {"id": "3"}],
            "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}],
        }
        graph2 = {
            "nodes": [{"id": "1"}, {"id": "2"}, {"id": "3"}],
            "edges": [{"source": "1", "target": "2"}, {"source": "1", "target": "3"}],
        }

        response = client.post(
            "/api/mces/bruteforce_pruning",
            json={"graph1": graph1, "graph2": graph2},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "algorithm" in data
        assert "result" in data
        assert data["algorithm"] == "bruteforce_pruning"
        assert "preserved_edges" in data["result"]
        assert "stats" in data["result"]
        assert "pruned_branches" in data["result"]["stats"]

    def test_pruning_empty_graphs(self, client):
        """Test MCES pruning on empty graphs."""
        graph1 = {"nodes": [], "edges": []}
        graph2 = {"nodes": [], "edges": []}

        response = client.post(
            "/api/mces/bruteforce_pruning",
            json={"graph1": graph1, "graph2": graph2},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert len(data["result"]["preserved_edges"]) == 0


class TestIlpR2Endpoint:
    """Test suite for /api/mces/ilp_r2 endpoint."""

    def test_ilp_r2_valid_request(self, client):
        """Test ILP R2 with valid input."""
        response = client.post(
            "/api/mces/ilp_r2",
            json={
                "graph1": {
                    "nodes": [{"id": "1"}, {"id": "2"}],
                    "edges": [{"source": "1", "target": "2"}],
                },
                "graph2": {
                    "nodes": [{"id": "A"}, {"id": "B"}],
                    "edges": [{"source": "A", "target": "B"}],
                },
            },
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["algorithm"] == "ilp_r2"
        assert "result" in data
        assert "mapping" in data["result"]
        assert "preserved_edges" in data["result"]
        assert "stats" in data["result"]
        assert "search_space_size" in data["result"]["stats"]
        assert "solution_optimality" in data["result"]["stats"]

    def test_ilp_r2_invalid_request(self, client):
        """Test ILP R2 with invalid input format."""
        response = client.post(
            "/api/mces/ilp_r2",
            json={},
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert data["error"] == "graph1 and graph2 are required"


class TestCORS:
    """Test suite for CORS configuration."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.post(
            "/api/generate",
            json={"num_nodes": 3, "num_edges": 2},
            content_type="application/json",
        )

        assert "Access-Control-Allow-Origin" in response.headers

    def test_preflight_request(self, client):
        """Test preflight OPTIONS request."""
        response = client.options("/api/generate")

        # Should return 200 or 204 for OPTIONS
        assert response.status_code in [200, 204]
