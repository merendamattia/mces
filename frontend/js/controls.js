// DOM elements
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
const algConnected = document.getElementById("alg-connected");
const algGreedyPath = document.getElementById("alg-greedy-path");
const selectAllAlgorithms = document.getElementById("select-all-algorithms");
const algoCheckboxes = document.querySelectorAll(".algo-checkbox");
const statsTableBody = document.getElementById("stats-table-body");
const statsTableHead = document.getElementById("stats-table-head");
// dynamic statistic column keys (excluding time_ms which has its own column)
let statColumns = [];

function resetStatsTableHeaders() {
  statColumns = [];
  if (!statsTableHead) return;
  // reset to base header: Algorithm | Preserved Edges | Time
  statsTableHead.innerHTML = `<tr><th>Algorithm</th><th>Preserved Edges</th><th>Time</th></tr>`;
}

function ensureStatColumns(keys) {
  if (!statsTableHead) return;
  const row = statsTableHead.querySelector('tr');
  keys.forEach((k) => {
    if (k === 'time_ms') return; // time is its own column
    if (!statColumns.includes(k)) {
      statColumns.push(k);
      const th = document.createElement('th');
      th.textContent = k.replace(/_/g, ' ');
      row.appendChild(th);

      // add placeholder cell to existing body rows
        Array.from(statsTableBody.children).forEach(r => {
          const td = document.createElement('td');
          td.textContent = '-';
          td.classList.add('numeric', 'monospace');
          r.appendChild(td);
        });
    }
  });
}

// initialize headers on load
resetStatsTableHeaders();

// Global state
let lastGraph1 = null;
let lastGraph2 = null;
let cachedPositions1 = null;
let cachedPositions2 = null;

/**
 * Generates and renders Graph 1 based on user input.
 * Clears cached positions and previous algorithm results.
 */
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
    algoResults.innerHTML = ""; // Clear previous results
    if (statsTableBody) statsTableBody.innerHTML = "";
    resetStatsTableHeaders();
  } catch (err) {
    alert(err.message || "Failed to generate Graph 1");
    console.error(err);
  } finally {
    generateG1Btn.disabled = false;
  }
}

/**
 * Generates and renders Graph 2 based on user input.
 * Clears cached positions and previous algorithm results.
 */
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
    algoResults.innerHTML = ""; // Clear previous results
    if (statsTableBody) statsTableBody.innerHTML = "";
    resetStatsTableHeaders();
  } catch (err) {
    alert(err.message || "Failed to generate Graph 2");
    console.error(err);
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

/**
 * Executes selected MCES algorithms on the two generated graphs.
 * Algorithms are run in parallel and results are rendered progressively as they complete.
 * This allows faster algorithms to display results immediately without waiting for slower ones.
 */
async function handleRunMces() {
  if (!lastGraph1 || !lastGraph2) {
    alert("Generate both graphs before running MCES.");
    return;
  }

  const selected = [];
  if (algBruteforce.checked) selected.push("bruteforce");
  if (algArcmatch.checked) selected.push("bruteforce_arcmatch");
  if (algConnected && algConnected.checked) selected.push("connected_mces");
  if (algGreedyPath && algGreedyPath.checked) selected.push("greedy_path_mces");

  if (selected.length === 0) {
    alert("Select at least one algorithm.");
    return;
  }

  runMcesBtn.disabled = true;
  algoResults.innerHTML = ""; // Clear previous results
  if (statsTableBody) statsTableBody.innerHTML = "";
  resetStatsTableHeaders();

  try {
    const promises = selected.map((alg) => {
      let promise;
      if (alg === "bruteforce") {
        promise = requestMcesBruteforce(lastGraph1, lastGraph2);
      } else if (alg === "bruteforce_arcmatch") {
        promise = requestMcesBruteforceArcmatch(lastGraph1, lastGraph2);
      } else if (alg === "connected_mces") {
        promise = requestMcesConnected(lastGraph1, lastGraph2);
      } else if (alg === "greedy_path_mces") {
        promise = requestMcesGreedyPath(lastGraph1, lastGraph2);
      } else {
        promise = Promise.reject(new Error("Unknown algorithm: " + alg));
      }

      // Render each result as soon as it arrives
      promise.then(result => {
        renderAlgorithmResult(result);
      }).catch(err => {
        console.error(`Error in ${alg}:`, err);
        // Re-throw so that Promise.all can detect the failure and the user is notified.
        throw err;
      });

      return promise;
    });

    // Wait for all to complete before re-enabling button
    await Promise.all(promises);
  } catch (err) {
    alert(err.message || "MCES request failed");
    console.error(err);
  } finally {
    runMcesBtn.disabled = false;
  }
}

/**
 * Renders the result of a single MCES algorithm.
 * Creates a result card with statistics and visualizes the preserved edges on both graphs.
 * Results are appended progressively as algorithms complete (no batching).
 *
 * @param {Object} entry - Algorithm result object containing algorithm name and result data
 * @param {string} entry.algorithm - Algorithm identifier ('bruteforce' or 'bruteforce_arcmatch')
 * @param {Object} entry.result - Result data including preserved_edges, mapping, and stats
 */
function renderAlgorithmResult(entry) {
  const colors = { bruteforce: "#0ea5e9", bruteforce_arcmatch: "#f97316", connected_mces: "#10b981", greedy_path_mces: "#8b5cf6" };
  const algoNames = { bruteforce: "Naïve Brute-Force", bruteforce_arcmatch: "Brute-Force + ArcMatch", connected_mces: "Connected MCES", greedy_path_mces: "Greedy Path MCES" };

  const { algorithm, result } = entry;
  const idx = algoResults.children.length; // Use current number of children as index
  const id1 = `alg-${idx}-g1`;
  const id2 = `alg-${idx}-g2`;
  const color = colors[algorithm] || "#3b5bfd";
  const algoName = algoNames[algorithm] || algorithm;
  const preservedCount = (result.preserved_edges || []).length;
  const stats = result.stats || {};

  // Append row to the statistics table (adds a new row as soon as an algorithm finishes)
  // Ensure header columns exist for the keys in stats (excluding time_ms)
  const statKeys = Object.keys(stats || {}).filter(k => k !== 'time_ms');
  ensureStatColumns(statKeys);

  if (statsTableBody) {
    const timeMs = stats.time_ms || null;
    const timeStr = timeMs != null ? (timeMs / 1000).toFixed(3) + 's' : '-';

    const row = document.createElement('tr');
    // base cells
    const algoTd = document.createElement('td'); algoTd.textContent = algoName;
    const preservedTd = document.createElement('td'); preservedTd.textContent = preservedCount; preservedTd.style.color = color;
    const timeTd = document.createElement('td'); timeTd.textContent = timeStr;
    // consistent classes for numeric/monospace alignment
    preservedTd.classList.add('preserved-count', 'numeric');
    timeTd.classList.add('numeric', 'monospace');
    row.appendChild(algoTd);
    row.appendChild(preservedTd);
    row.appendChild(timeTd);

    // stat columns in order of statColumns
    statColumns.forEach((col) => {
      const td = document.createElement('td');
      const v = stats[col];
      if (v == null) {
        td.textContent = '-';
      } else if (typeof v === 'number') {
        td.textContent = Number.isInteger(v) ? v : v.toFixed(2);
        td.classList.add('numeric', 'monospace');
      } else {
        td.textContent = String(v);
      }
      row.appendChild(td);
    });

    statsTableBody.appendChild(row);
  }

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

  const card = `<div class="result-card">
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

  algoResults.insertAdjacentHTML('beforeend', card);

  // Render graphs with highlights
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

  renderGraph(id1, lastGraph1, "graph1", highlight1Local, cachedPositions1);
  renderGraph(id2, lastGraph2, "graph2", highlight2Local, cachedPositions2);
}
