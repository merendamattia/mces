const API_BASE = "http://localhost:5001"; // Backend Flask server (default)

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
