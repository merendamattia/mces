const numNodesInput = document.getElementById("num-nodes");
const numEdgesInput = document.getElementById("num-edges");
const generateBtn = document.getElementById("generate-btn");
const statusEl = document.getElementById("status");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? "#b91c1c" : "#52606d";
}

async function handleGenerate() {
  const numNodes = parseInt(numNodesInput.value, 10);
  const numEdges = parseInt(numEdgesInput.value, 10);

  if (Number.isNaN(numNodes) || Number.isNaN(numEdges)) {
    setStatus("Please enter valid numbers.", true);
    return;
  }

  setStatus("Generating graphs...");
  generateBtn.disabled = true;

  try {
    const result = await requestGraphs(numNodes, numEdges);
    renderGraphs(result.graph1, result.graph2);
    setStatus("Graphs updated.");
  } catch (err) {
    setStatus(err.message || "Request failed", true);
  } finally {
    generateBtn.disabled = false;
  }
}

generateBtn.addEventListener("click", handleGenerate);

// Initial render to show default parameters quickly.
handleGenerate();
