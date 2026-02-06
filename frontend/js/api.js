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

/**
 * Executes the Connected MCES algorithm on two graphs.
 * This algorithm uses backtracking to find connected common edge subgraphs.
 *
 * @param {Object} graph1 - First graph object with nodes and edges
 * @param {Object} graph2 - Second graph object with nodes and edges
 * @returns {Promise<Object>} Response containing algorithm results (preserved_edges, mapping, stats)
 * @throws {Error} If the request fails or returns an error
 */
async function requestMcesConnected(graph1, graph2) {
  const response = await fetch(`${API_BASE}/api/mces/connected`, {
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
 * Executes the Greedy Path MCES algorithm on two graphs.
 * This heuristic algorithm finds common edge subgraphs by exploring paths greedily.
 *
 * @param {Object} graph1 - First graph object with nodes and edges
 * @param {Object} graph2 - Second graph object with nodes and edges
 * @param {number} maxPathLen - Maximum path length to explore (default: 4)
 * @returns {Promise<Object>} Response containing algorithm results (preserved_edges, mapping, stats)
 * @throws {Error} If the request fails or returns an error
 */
async function requestMcesGreedyPath(graph1, graph2, maxPathLen = 4) {
  const response = await fetch(`${API_BASE}/api/mces/greedy_path`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ graph1, graph2, max_path_len: maxPathLen })
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Request failed" }));
    throw new Error(error.error || "Request failed");
  }
  return response.json();
}

/**
 * Executes the ILP R2 MCES algorithm on two graphs.
 * This algorithm uses Integer Linear Programming to find the Maximum Common Edge Subgraph.
 *
 * @param {Object} graph1 - First graph object with nodes and edges
 * @param {Object} graph2 - Second graph object with nodes and edges
 * @returns {Promise<Object>} Response containing algorithm results (preserved_edges, mapping, stats)
 * @throws {Error} If the request fails or returns an error
 */
async function requestMcesIlpR2(graph1, graph2) {
  const response = await fetch(`${API_BASE}/api/mces/ilp_r2`, {
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
 * Executes the Simulated Annealing MCES algorithm on two graphs.
 * This metaheuristic algorithm uses simulated annealing to find common edge subgraphs.
 *
 * @param {Object} graph1 - First graph object with nodes and edges
 * @param {Object} graph2 - Second graph object with nodes and edges
 * @param {number} initialTemperature - Initial temperature for annealing (default: 100.0)
 * @param {number} coolingRate - Cooling rate for annealing (default: 0.95)
 * @param {number} maxIterations - Maximum number of iterations (default: 1000)
 * @returns {Promise<Object>} Response containing algorithm results (preserved_edges, mapping, stats)
 * @throws {Error} If the request fails or returns an error
 */
async function requestMcesSimulatedAnnealing(graph1, graph2, initialTemperature = 100.0, coolingRate = 0.95, maxIterations = 1000) {
  const response = await fetch(`${API_BASE}/api/mces/simulated_annealing`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      graph1,
      graph2,
      initial_temperature: initialTemperature,
      cooling_rate: coolingRate,
      max_iterations: maxIterations
    })
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Request failed" }));
    throw new Error(error.error || "Request failed");
  }

  return response.json();
}
