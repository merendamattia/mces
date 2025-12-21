/**
 * Clears all child elements from an SVG element.
 *
 * @param {SVGElement} svgElement - The SVG element to clear
 */
function clearGraph(svgElement) {
  while (svgElement.firstChild) {
    svgElement.removeChild(svgElement.firstChild);
  }
}

/**
 * Renders a graph in an SVG element with optional highlighted edges.
 * Uses either cached positions or computes new layout using Fruchterman-Reingold algorithm.
 * Highlighted edges and their connected nodes are drawn with specified colors.
 *
 * @param {string} svgId - The ID of the SVG element to render into
 * @param {Object} graphData - Graph data containing nodes and edges arrays
 * @param {string} colorClass - CSS class for edge coloring
 * @param {Array} highlightEdges - Array of edges to highlight with optional color property
 * @param {Map} cachedPositions - Optional cached node positions to maintain stable layout
 * @returns {Map} Map of node IDs to {x, y} positions for caching
 */
function renderGraph(svgId, graphData, colorClass, highlightEdges = [], cachedPositions = null) {
  const svg = document.getElementById(svgId);
  if (!svg || !graphData) return null;

  clearGraph(svg);
  const width = svg.clientWidth;
  const height = svg.clientHeight;

  const nodes = graphData.nodes || [];
  const edges = graphData.edges || [];

  const positions = cachedPositions || computeFrLayout(nodes, edges, width, height);

  edges.forEach((edge) => {
    const source = positions.get(edge.source);
    const target = positions.get(edge.target);
    if (!source || !target) return;

    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", source.x);
    line.setAttribute("y1", source.y);
    line.setAttribute("x2", target.x);
    line.setAttribute("y2", target.y);
    line.setAttribute("class", `edge ${colorClass}`);
    svg.appendChild(line);
  });

  // Highlighted edges overlaid for algorithm results.
  const highlightNodes = new Map(); // nodeId -> color
  highlightEdges.forEach((edge) => {
    const source = positions.get(edge.source);
    const target = positions.get(edge.target);
    if (!source || !target) return;
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", source.x);
    line.setAttribute("y1", source.y);
    line.setAttribute("x2", target.x);
    line.setAttribute("y2", target.y);
    line.setAttribute("class", "edge highlight");
    const color = edge.color || "#3b5bfd";
    line.setAttribute("stroke", color);
    svg.appendChild(line);

    if (!highlightNodes.has(edge.source)) highlightNodes.set(edge.source, color);
    if (!highlightNodes.has(edge.target)) highlightNodes.set(edge.target, color);
  });

  nodes.forEach((node) => {
    const pos = positions.get(node.id);
    if (!pos) return;

    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", pos.x);
    circle.setAttribute("cy", pos.y);
    circle.setAttribute("r", 12);
    const color = highlightNodes.get(node.id);
    if (highlightNodes.has(node.id)) {
      circle.setAttribute("class", "node highlight");
      if (color) {
        circle.style.fill = color;
        circle.style.stroke = color;
      }
    } else {
      circle.setAttribute("class", "node dim");
    }

    svg.appendChild(circle);
  });

  return positions;
}

/**
 * Renders two graphs side by side with optional highlighting.
 *
 * @param {Object} graph1 - First graph data
 * @param {Object} graph2 - Second graph data
 * @param {Array} highlight1 - Edges to highlight in graph1
 * @param {Array} highlight2 - Edges to highlight in graph2
 * @returns {Object} Object containing positions1 and positions2 Maps
 */
function renderGraphs(graph1, graph2, highlight1 = [], highlight2 = []) {
  const positions1 = renderGraph("graph1", graph1, "graph1", highlight1);
  const positions2 = renderGraph("graph2", graph2, "graph2", highlight2);
  return { positions1, positions2 };
}

/**
 * Computes graph layout using Fruchterman-Reingold force-directed algorithm.
 * Nodes repel each other while edges act as springs pulling connected nodes together.
 * Uses simulated annealing with decreasing temperature for stable convergence.
 *
 * @param {Array} nodes - Array of node objects with id property
 * @param {Array} edges - Array of edge objects with source and target properties
 * @param {number} width - Width of the layout area
 * @param {number} height - Height of the layout area
 * @returns {Map} Map of node IDs to {x, y} positions
 */
function computeFrLayout(nodes, edges, width, height) {
  // Fruchterman-Reingold style force layout (similar spirit to graphviz "sfdp" but lightweight).
  const positions = new Map();
  const disp = new Map();
  const margin = 24;
  const area = width * height;
  const k = Math.sqrt(area / Math.max(nodes.length, 1));

  nodes.forEach((node) => {
    positions.set(node.id, {
      x: margin + Math.random() * (width - 2 * margin),
      y: margin + Math.random() * (height - 2 * margin)
    });
    disp.set(node.id, { x: 0, y: 0 });
  });

  const iterations = 200;
  let temperature = Math.min(width, height) / 8;
  const cool = temperature / iterations;

  for (let iter = 0; iter < iterations; iter++) {
    // Reset displacement
    nodes.forEach((node) => {
      const d = disp.get(node.id);
      d.x = 0;
      d.y = 0;
    });

    // Repulsive forces
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const u = positions.get(nodes[i].id);
        const v = positions.get(nodes[j].id);
        if (!u || !v) continue;
        let dx = u.x - v.x;
        let dy = u.y - v.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
        const force = (k * k) / dist;
        dx = (dx / dist) * force;
        dy = (dy / dist) * force;
        const du = disp.get(nodes[i].id);
        const dv = disp.get(nodes[j].id);
        du.x += dx;
        du.y += dy;
        dv.x -= dx;
        dv.y -= dy;
      }
    }

    // Attractive forces
    edges.forEach((edge) => {
      const u = positions.get(edge.source);
      const v = positions.get(edge.target);
      if (!u || !v) return;
      let dx = u.x - v.x;
      let dy = u.y - v.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
      const force = (dist * dist) / k;
      dx = (dx / dist) * force;
      dy = (dy / dist) * force;
      const du = disp.get(edge.source);
      const dv = disp.get(edge.target);
      du.x -= dx;
      du.y -= dy;
      dv.x += dx;
      dv.y += dy;
    });

    // Limit by temperature and keep inside viewport
    nodes.forEach((node) => {
      const pos = positions.get(node.id);
      const d = disp.get(node.id);
      const dist = Math.sqrt(d.x * d.x + d.y * d.y) || 0.01;
      const limited = Math.min(dist, temperature);
      pos.x += (d.x / dist) * limited;
      pos.y += (d.y / dist) * limited;
      pos.x = Math.min(width - margin, Math.max(margin, pos.x));
      pos.y = Math.min(height - margin, Math.max(margin, pos.y));
    });

    temperature = Math.max(0, temperature - cool);
  }

  return positions;
}
