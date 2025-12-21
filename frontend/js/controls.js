const numNodesG1Input = document.getElementById("num-nodes-g1");
const numEdgesG1Input = document.getElementById("num-edges-g1");
const generateG1Btn = document.getElementById("generate-g1-btn");
const numNodesG2Input = document.getElementById("num-nodes-g2");
const numEdgesG2Input = document.getElementById("num-edges-g2");
const generateG2Btn = document.getElementById("generate-g2-btn");
const runMcesBtn = document.getElementById("run-mces-btn");
const algoResults = document.getElementById("algo-results");
const algBruteforce = document.getElementById("alg-bruteforce");
const algArcmatch = document.getElementById("alg-bruteforce-arcmatch");
const selectAllAlgorithms = document.getElementById("select-all-algorithms");
const algoCheckboxes = document.querySelectorAll(".algo-checkbox");

let lastGraph1 = null;
let lastGraph2 = null;
let cachedPositions1 = null;
let cachedPositions2 = null;

async function handleGenerateGraph1() {
  const numNodes = parseInt(numNodesG1Input.value, 10);
  const numEdges = parseInt(numEdgesG1Input.value, 10);

  if (Number.isNaN(numNodes) || Number.isNaN(numEdges)) {
    alert("Please enter valid numbers for Graph 1");
    return;
  }

  generateG1Btn.disabled = true;
  try {
    const result = await requestGraphs(numNodes, numEdges);
    lastGraph1 = result.graph1;
    cachedPositions1 = null;
    const positions1 = renderGraph("graph1", lastGraph1, "graph1", []);
    cachedPositions1 = positions1;
    renderAlgorithmResults([]);
  } catch (err) {
    alert(err.message || "Failed to generate Graph 1");
  } finally {
    generateG1Btn.disabled = false;
  }
}

async function handleGenerateGraph2() {
  const numNodes = parseInt(numNodesG2Input.value, 10);
  const numEdges = parseInt(numEdgesG2Input.value, 10);

  if (Number.isNaN(numNodes) || Number.isNaN(numEdges)) {
    alert("Please enter valid numbers for Graph 2");
    return;
  }

  generateG2Btn.disabled = true;
  try {
    const result = await requestGraphs(numNodes, numEdges);
    lastGraph2 = result.graph1; // Use graph1 from result since we're calling with different params
    cachedPositions2 = null;
    const positions2 = renderGraph("graph2", lastGraph2, "graph2", []);
    cachedPositions2 = positions2;
    renderAlgorithmResults([]);
  } catch (err) {
    alert(err.message || "Failed to generate Graph 2");
  } finally {
    generateG2Btn.disabled = false;
  }
}

generateG1Btn.addEventListener("click", handleGenerateGraph1);
generateG2Btn.addEventListener("click", handleGenerateGraph2);
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
handleGenerateGraph1().then(() => handleGenerateGraph2());

async function handleRunMces() {
  if (!lastGraph1 || !lastGraph2) {
    alert("Generate both graphs before running MCES.");
    return;
  }

  const selected = [];
  if (algBruteforce.checked) selected.push("bruteforce");
  if (algArcmatch.checked) selected.push("bruteforce_arcmatch");

  if (selected.length === 0) {
    alert("Select at least one algorithm.");
    return;
  }

  runMcesBtn.disabled = true;

  try {
    const promises = selected.map((alg) => {
      if (alg === "bruteforce") return requestMcesBruteforce(lastGraph1, lastGraph2);
      return requestMcesBruteforceArcmatch(lastGraph1, lastGraph2);
    });

    const results = await Promise.all(promises);

    renderAlgorithmResults(results);
  } catch (err) {
    alert(err.message || "MCES request failed");
  } finally {
    runMcesBtn.disabled = false;
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

      // Build stats list
      const statsList = Object.entries(stats)
        .map(([k, v]) => {
          let label = k.replace(/_/g, " ");
          let value = v;

          // Convert time_ms to seconds with 3 decimals
          if (k === "time_ms") {
            label = "Time";
            value = (v / 1000).toFixed(3) + "s";
          } else if (typeof v === "number") {
            value = Number.isInteger(v) ? v : v.toFixed(2);
          }

          label = label.charAt(0).toUpperCase() + label.slice(1);

          return `<div class="stat-item"><span class="stat-label">${label}:</span> <span class="stat-value">${value}</span></div>`;
        })
        .join("");

      return `<div class="result-card">
          <div class="result-header">
            <h3 style="color: ${color}">${algoName}</h3>
            <div class="result-stats">
              <div class="stat-item main"><span class="stat-label">Preserved Edges:</span> <span class="stat-value" style="color: ${color}">${preservedCount}</span></div>
              ${statsList}
            </div>
          </div>
          <div class="result-graphs">
            <div class="graph-panel">
              <h4>Graph 1</h4>
              <svg id="${id1}" class="graph-canvas" role="img" aria-label="${algoName} Graph 1"></svg>
            </div>
            <div class="graph-panel">
              <h4>Graph 2</h4>
              <svg id="${id2}" class="graph-canvas" role="img" aria-label="${algoName} Graph 2"></svg>
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
