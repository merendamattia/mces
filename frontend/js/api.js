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
