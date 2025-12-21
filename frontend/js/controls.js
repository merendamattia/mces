const numNodesInput = document.getElementById("num-nodes");
const numEdgesInput = document.getElementById("num-edges");
const generateBtn = document.getElementById("generate-btn");
const runMcesBtn = document.getElementById("run-mces-btn");
const statusEl = document.getElementById("status");
const algoResults = document.getElementById("algo-results");
const algBruteforce = document.getElementById("alg-bruteforce");
const algArcmatch = document.getElementById("alg-bruteforce-arcmatch");
const selectAllAlgorithms = document.getElementById("select-all-algorithms");
const algoCheckboxes = document.querySelectorAll(".algo-checkbox");

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

// Select all algorithms handler
selectAllAlgorithms.addEventListener("change", function() {
  algoCheckboxes.forEach(cb => cb.checked = this.checked);
});

// Update select all state when individual checkboxes change
algoCheckboxes.forEach(cb => {
  cb.addEventListener("change", function() {
    const allChecked = Array.from(algoCheckboxes).every(c => c.checked);
    const someChecked = Array.from(algoCheckboxes).some(c => c.checked);
    selectAllAlgorithms.checked = allChecked;
    selectAllAlgorithms.indeterminate = someChecked && !allChecked;
  });
});

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

      // Build stats badges
      const statsBadges = Object.entries(stats)
        .map(([k, v]) => {
          let label = k.replace(/_/g, " ");
          let value = v;

          // Convert time_ms to seconds with 3 decimals
          if (k === "time_ms") {
            label = "time";
            value = (v / 1000).toFixed(3) + "s";
          } else if (typeof v === "number") {
            value = Number.isInteger(v) ? v : v.toFixed(2);
          }

          const icon = k === 'time_ms' ? 'clock' : k.includes('explored') ? 'search' : k.includes('recursive') ? 'arrow-repeat' : k.includes('pruned') ? 'scissors' : 'check-circle';
          return `<span class="badge bg-secondary me-2 mb-2"><i class="bi bi-${icon}"></i> ${label}: <strong>${value}</strong></span>`;
        })
        .join("");

      return `<div class="result-card card shadow-sm mb-4">
        <div class="card-body">
          <h3 class="card-title" style="color: ${color}"><i class="bi bi-cpu"></i> ${algoName}</h3>
          <div class="result-content">
            <div class="result-info mb-3">
              <h4 class="mb-3"><i class="bi bi-diagram-3"></i> Preserved Edges: <span class="badge" style="background-color: ${color}; font-size: 1.2rem;">${preservedCount}</span></h4>
              <div class="result-section">
                <h5 class="mb-2"><i class="bi bi-bar-chart"></i> Statistics</h5>
                <div class="stats-badges">${statsBadges}</div>
              </div>
            </div>
            <div class="result-graphs">
              <div class="graph-panel card">
                <div class="card-header"><h4 class="mb-0"><i class="bi bi-diagram-2"></i> Graph 1</h4></div>
                <div class="card-body graph-canvas-container">
                  <svg id="${id1}" class="graph-canvas" role="img" aria-label="${algoName} Graph 1"></svg>
                </div>
              </div>
              <div class="graph-panel card">
                <div class="card-header"><h4 class="mb-0"><i class="bi bi-diagram-2"></i> Graph 2</h4></div>
                <div class="card-body graph-canvas-container">
                  <svg id="${id2}" class="graph-canvas" role="img" aria-label="${algoName} Graph 2"></svg>
                </div>
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
