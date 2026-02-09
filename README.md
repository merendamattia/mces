# MCES - Maximum Common Edge Subgraph

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Latest Release](https://img.shields.io/github/v/release/merendamattia/mces?label=release)](https://github.com/merendamattia/mces/releases)

Implementation and benchmarking of algorithms for the **Maximum Common Edge Subgraph (MCES)** problem with interactive web visualizer.

## The MCES Problem

The Maximum Common Edge Subgraph (MCES) problem is a fundamental problem in graph theory: given two graphs $G_1$ and $G_2$, find a common subgraph $H$ with the **maximum number of edges** that is isomorphic to both a subgraph of $G_1$ and a subgraph of $G_2$.

### Complexity and Applications

- **NP-complete** for general graphs
- **APX-hard**: difficult to approximate within a constant factor
- Generalizes well-known problems such as maximum clique and subgraph isomorphism

**Practical applications:**
- **Computational chemistry**: Comparison of molecular structures and similarity between compounds
- **Biology**: Network alignment for protein networks across species
- **Pattern recognition**: Object recognition in images
- **Social network analysis**: Study of common structures in social networks

## Implemented Algorithms

The project includes six algorithms covering the entire spectrum of approaches:

1. **Brute Force** - Complete enumeration (baseline)
2. **Brute Force with Pruning + Backtracking** - With intelligent pruning
3. **Connected MCES** - Guarantees connected subgraphs
4. **Greedy Path** - Fast constructive heuristic based on paths
5. **ILP R2** - Integer Linear Programming with PuLP solver
6. **Simulated Annealing** - Metaheuristic for large graphs

Each algorithm returns:
- Node mapping between the two graphs
- Preserved edges in the common subgraph
- Detailed statistics (time, explored space, optimality, memory)

## Benchmark

### Running the Benchmark

The benchmark systematically compares all algorithms on graphs of varying sizes:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the benchmark
python benchmark.py
```

**Configurable parameters** (modifiable at the top of `benchmark.py`):
- `N_MIN`, `N_MAX`: Node range (default: 7-12)
- `EDGE_MULTIPLIERS`: Edge density (default: [1.2, 1.5, 2.0])
- `REPEATS`: Repetitions per configuration (default: 5)
- `PER_CALL_TIMEOUT`: Timeout per algorithm in seconds (default: 300)
- `RANDOM_SEED`: Seed for reproducibility (default: 9871)

The benchmark generates:
- `results/YYYYMMDD-HHMMSS/benchmark_results.csv` - Detailed results
- `results/YYYYMMDD-HHMMSS/metadata.json` - Exact execution configuration

### Visualizing Results

After running the benchmark, generate analysis plots:

```bash
python plot.py results/YYYYMMDD-HHMMSS/benchmark_results.csv
```

Replace `YYYYMMDD-HHMMSS` with your actual results timestamp folder. This creates SVG plots in the `results/YYYYMMDD-HHMMSS/graphs/` folder:
- `performance_summary.svg` - Overall performance comparison
- `time_vs_graph_size.svg` - Scalability with number of nodes
- `time_vs_edges.svg` - Effect of graph density
- `heatmap_time_by_size.svg` - Heatmap of execution times
- `solution_quality.svg` - Quality of solutions found
- `search_space_exploration.svg` - Search space explored
- `timeout_analysis.svg` - Timeout analysis per algorithm

### Benchmark Features

- **Parallelization**: 5 worker threads for concurrent executions
- **Robust timeouts**: Each algorithm executed in separate process with forced termination
- **Reproducibility**: Fixed seed, complete metadata, Docker support
- **Complete metrics**: Time, memory, explored space, optimality
- **Incremental output**: CSV written in real-time with file locking

## Interactive Visualizer

The project also includes a web interface to generate and visualize graphs interactively.

### Running with Docker (Recommended)

```bash
docker compose up
```

Access at:
- **Frontend**: http://localhost:8000
- **Backend API**: http://localhost:5001

### Running Manually

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**Frontend:**
```bash
cd frontend
python -m http.server 8000
```

Open http://localhost:8000 in your browser.

### Visualizer Features

- Random graph generation with configurable parameters
- Side-by-side visualization with force-directed layout
- Real-time MCES algorithm execution (for small graphs)
- Mapping and preserved edges visualization
- Performance statistics

## Conventional Commits

The project follows the Conventional Commits specification. Install git hooks:

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

## API Contract

### POST /api/generate

**Request:**
```json
{
  "num_nodes": 8,
  "num_edges": 12,
  "algorithm": "bruteforce_pruning"
}
```

**Available algorithms:**
- `"none"` - Graph generation only
- `"bruteforce"` - Complete brute force
- `"bruteforce_pruning"` - With pruning
- `"connected_mces"` - Connected subgraphs
- `"greedy_path_mces"` - Greedy heuristic
- `"ilp_r2"` - Integer Linear Programming
- `"simulated_annealing"` - Simulated Annealing

**Response:**
```json
{
  "graph1": {
    "nodes": [{"id": "1"}, {"id": "2"}],
    "edges": [{"source": "1", "target": "2"}]
  },
  "graph2": { "nodes": [...], "edges": [...] },
  "mces": {
    "algorithm": "bruteforce_pruning",
    "result": {
      "mapping": {"1": "3", "2": "4"},
      "preserved_edges": [["1", "2"]],
      "stats": {
        "time_ms": 1.2,
        "mappings_explored": 120,
        "recursive_calls": 45,
        "pruned_branches": 30,
        "memory_usage_mb": 2.5,
        "solution_optimality": true
      }
    }
  }
}
```

**Notes:**
- Undirected graphs with string node IDs
- Nessun self-loop o archi duplicati
- Con `num_nodes > 1`, ogni nodo ha almeno un arco

## Testing

```bash
cd backend
pytest
```

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.

## References

- Bahiense, L., et al. (2012). "The maximum common edge subgraph problem: A polyhedral investigation"
- Larsen, S. J., et al. (2016). "A Simulated Annealing Algorithm for Maximum Common Edge Subgraph Detection"
- Akutsu, T., & Tamura, T. (2013). "A Polynomial-Time Algorithm for Computing the Maximum Common Connected Edge Subgraph"

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
