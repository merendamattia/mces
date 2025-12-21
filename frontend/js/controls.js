const numNodesInput = document.getElementById("num-nodes");
const numEdgesInput = document.getElementById("num-edges");
const generateBtn = document.getElementById("generate-btn");
const runMcesBtn = document.getElementById("run-mces-btn");
const statusEl = document.getElementById("status");
const algoResults = document.getElementById("algo-results");
const algBruteforce = document.getElementById("alg-bruteforce");
const algArcmatch = document.getElementById("alg-bruteforce-arcmatch");

let lastGraph1 = null;
let lastGraph2 = null;
let cachedPositions1 = null;
let cachedPositions2 = null;

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
  runMcesBtn.disabled = true;

  try {
    const result = await requestGraphs(numNodes, numEdges);
    lastGraph1 = result.graph1;
    lastGraph2 = result.graph2;
    // Reset cached positions when new graphs are generated
    cachedPositions1 = null;
    cachedPositions2 = null;
    const positions = renderGraphs(lastGraph1, lastGraph2);
    cachedPositions1 = positions.positions1;
    cachedPositions2 = positions.positions2;
    renderAlgorithmResults([]);
    setStatus("Graphs updated.");
  } catch (err) {
    setStatus(err.message || "Request failed", true);
  } finally {
    generateBtn.disabled = false;
    runMcesBtn.disabled = false;
  }
}

generateBtn.addEventListener("click", handleGenerate);
runMcesBtn.addEventListener("click", handleRunMces);

// Initial render to show default parameters quickly.
handleGenerate();

async function handleRunMces() {
  if (!lastGraph1 || !lastGraph2) {
    setStatus("Generate graphs before running MCES.", true);
    return;
  }

  const selected = [];
  if (algBruteforce.checked) selected.push("bruteforce");
  if (algArcmatch.checked) selected.push("bruteforce_arcmatch");

  if (selected.length === 0) {
    setStatus("Select at least one algorithm.", true);
    return;
  }

  setStatus("Running MCES...");
  runMcesBtn.disabled = true;
  generateBtn.disabled = true;

  try {
    const promises = selected.map((alg) => {
      if (alg === "bruteforce") return requestMcesBruteforce(lastGraph1, lastGraph2);
      return requestMcesBruteforceArcmatch(lastGraph1, lastGraph2);
    });

    const results = await Promise.all(promises);

    renderGraphs(lastGraph1, lastGraph2);
    renderAlgorithmResults(results);
    setStatus("MCES completed.");
  } catch (err) {
    setStatus(err.message || "MCES request failed", true);
  } finally {
    runMcesBtn.disabled = false;
    generateBtn.disabled = false;
  }
}

function renderAlgorithmResults(results) {
  if (!results || results.length === 0) {
    algoResults.innerHTML = "";
    return;
  }

  const colors = { bruteforce: "#0ea5e9", bruteforce_arcmatch: "#f97316" };
  const algoNames = { bruteforce: "Naïve Brute-Force", bruteforce_arcmatch: "Brute-Force + ArcMatch" };

  const cards = results
    .map((entry, idx) => {
      const { algorithm, result } = entry;
      const id1 = `alg-${idx}-g1`;
      const id2 = `alg-${idx}-g2`;
      const color = colors[algorithm] || "#3b5bfd";
      const algoName = algoNames[algorithm] || algorithm;
      const preservedCount = (result.preserved_edges || []).length;
      const stats = result.stats || {};

      // Build stats table
      const statsRows = Object.entries(stats)
        .map(([k, v]) => {
          const label = k.replace(/_/g, " ");
          const value = typeof v === "number" ? (Number.isInteger(v) ? v : v.toFixed(2)) : v;
          return `<tr><td>${label}</td><td>${value}</td></tr>`;
        })
        .join("");
      const statsTable = `<table class="stats-table"><tbody>${statsRows}</tbody></table>`;

      return `<div class="result-card">
        <h3 style="color: ${color}">${algoName}</h3>
        <div class="result-content">
          <div class="result-info">
            <h4>Preserved Edges: <span class="highlight-value" style="color: ${color}">${preservedCount}</span></h4>
            <div class="result-section">
              <h5>Statistics</h5>
              ${statsTable}
            </div>
          </div>
          <div class="result-graphs">
            <div class="graph-panel">
              <h4>Graph 1</h4>
              <div class="graph-canvas-container">
                <svg id="${id1}" class="graph-canvas" role="img" aria-label="${algoName} Graph 1"></svg>
              </div>
            </div>
            <div class="graph-panel">
              <h4>Graph 2</h4>
              <div class="graph-canvas-container">
                <svg id="${id2}" class="graph-canvas" role="img" aria-label="${algoName} Graph 2"></svg>
              </div>
            </div>
          </div>
        </div>
      </div>`;
    })
    .join("");

  algoResults.innerHTML = cards;

  // After DOM insert, render each pair with its highlights.
  results.forEach((entry, idx) => {
    const { algorithm, result } = entry;
    const color = colors[algorithm] || "#3b5bfd";
    const preserved = result.preserved_edges || [];
    const mapping = result.mapping || {};

    const highlight1Local = preserved.map(([u, v]) => ({ source: u, target: v, color }));
    const highlight2Local = preserved
      .map(([u, v]) => {
        const mu = mapping[u];
        const mv = mapping[v];
        if (mu && mv) return { source: mu, target: mv, color };
        return null;
      })
      .filter(Boolean);

    renderGraph(`alg-${idx}-g1`, lastGraph1, "graph1", highlight1Local, cachedPositions1);
    renderGraph(`alg-${idx}-g2`, lastGraph2, "graph2", highlight2Local, cachedPositions2);
  });
}
