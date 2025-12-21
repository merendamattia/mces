# MCES Visualizer

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Latest Release](https://img.shields.io/github/v/release/merendamattia/mces?label=release)](https://github.com/merendamattia/mces/releases)

Academic prototype for experimenting with the **Maximum Common Edge-Subgraph (MCES)** problem. This first draft focuses on infrastructure: a Flask backend, a browser-based frontend, and interactive generation/visualization of two random graphs.

## Conventional commits & hooks

This project follows the Conventional Commits specification. Please install the Git commit hooks before making commits:

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

## Running the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The API will listen on `http://localhost:5001` by default (set `PORT` to override) and expose `POST /api/generate`.

### API contract (current draft)
- **POST /api/generate**
- Request JSON:
  ```json
  { "num_nodes": <int>, "num_edges": <int> }
  ```
- Response JSON:
  ```json
  {
    "graph1": { "nodes": [{"id": "1"}], "edges": [{"source": "1", "target": "2"}] },
    "graph2": { "nodes": [...], "edges": [...] }
  }
  ```

Graphs are undirected, have string node IDs, avoid self-loops and duplicate edges.
When `num_nodes > 1` the generator ensures every node has at least one incident edge; if the requested edge count is too low, it is raised to the minimum needed.

## Running the frontend

Serve the static files so the browser can reach `/api/generate` on the same host. From `frontend/` you can run a simple server:

```bash
cd frontend
python -m http.server 8000
```

Then open `http://localhost:8000` in your browser. The backend enables permissive CORS for this prototype so the frontend can call `http://localhost:5001/api/generate` from a different port. The page will:
- let you set node and edge counts,
- call the backend to generate two independent random graphs,
- render both graphs side by side using SVG with a Fruchterman–Reingold-style force layout.
