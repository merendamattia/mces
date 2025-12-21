// Backend Flask server base URL
const API_BASE = "http://localhost:5001";

/**
 * Requests generation of random graphs from the backend.
 *
 * @param {number} numNodes - Number of nodes to generate
 * @param {number} numEdges - Number of edges to generate
 * @returns {Promise<Object>} Response containing graph1 and graph2 objects
 * @throws {Error} If the request fails or returns an error
 */
async function requestGraphs(numNodes, numEdges) {
  const response = await fetch(`${API_BASE}/api/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ num_nodes: numNodes, num_edges: numEdges })
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Request failed" }));
    throw new Error(error.error || "Request failed");
  }

  return response.json();
}

/**
 * Executes the Naïve Brute-Force MCES algorithm on two graphs.
 * This algorithm explores all possible node mappings without pruning.
 *
 * @param {Object} graph1 - First graph object with nodes and edges
 * @param {Object} graph2 - Second graph object with nodes and edges
 * @returns {Promise<Object>} Response containing algorithm results (preserved_edges, mapping, stats)
 * @throws {Error} If the request fails or returns an error
 */
async function requestMcesBruteforce(graph1, graph2) {
  const response = await fetch(`${API_BASE}/api/mces/bruteforce`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ graph1, graph2 })
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Request failed" }));
    throw new Error(error.error || "Request failed");
  }
  return response.json();
}

/**
 * Executes the Brute-Force + ArcMatch MCES algorithm on two graphs.
 * This algorithm uses ArcMatch pruning to eliminate impossible branches early,
 * significantly improving performance over naive brute-force.
 *
 * @param {Object} graph1 - First graph object with nodes and edges
 * @param {Object} graph2 - Second graph object with nodes and edges
 * @returns {Promise<Object>} Response containing algorithm results (preserved_edges, mapping, stats)
 * @throws {Error} If the request fails or returns an error
 */
async function requestMcesBruteforceArcmatch(graph1, graph2) {
  const response = await fetch(`${API_BASE}/api/mces/bruteforce_arcmatch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ graph1, graph2 })
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Request failed" }));
    throw new Error(error.error || "Request failed");
  }
  return response.json();
}
