#!/usr/bin/env python3
"""Benchmark runner for MCES algorithms.

Generates random graph pairs and runs each algorithm with a per-call timeout.
Saves a CSV with one row per algorithm run containing all available statistics.

Parameters at top of file are easily configurable.
"""
from __future__ import annotations

import csv
import datetime
import fcntl
import multiprocessing as mp
import os
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Tuple

repo_root = pathlib.Path(__file__).resolve().parent
backend_path = str(repo_root / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from backend.algorithms import (
    compute_mces_bruteforce,
    compute_mces_bruteforce_arcmatch,
    compute_mces_connected,
    compute_mces_greedy_path,
)
from backend.core.generator import generate_random_graph_pair

# -------------------- Configurable parameters --------------------
# Nodes range (inclusive)
N_MIN = 7
N_MAX = 12
# Number of random repeats per (n, m) pair
REPEATS = 5
# Edges selection strategy: multipliers applied to n (will be clipped to valid range)
EDGE_MULTIPLIERS = [1, 2, 3]
# Per-algorithm timeout in seconds
PER_CALL_TIMEOUT = 300
# Output CSV file
OUTPUT_CSV = "benchmark_results.csv"
# Top-level results folder
RESULTS_ROOT = "results"
# Thread pool max workers for concurrent runs
MAX_WORKERS = 6
# Random seed for reproducibility (None for random)
RANDOM_SEED = 42
# -----------------------------------------------------------------


def _run_algorithm_in_process(target_fn, g1, g2, out_queue: mp.Queue) -> None:
    """Worker wrapper executed in a separate process.

    Runs the target function and puts the result (or exception info) into the queue.
    """
    try:
        res = target_fn(g1, g2)
        out_queue.put(("ok", res))
    except Exception as e:  # pragma: no cover - defensive
        out_queue.put(("error", repr(e)))


def call_with_timeout(target_fn, g1, g2, timeout: float) -> Tuple[bool, Any]:
    """Call target_fn(g1,g2) in separate process and enforce timeout.

    Returns (finished, result). If finished is False the result is a string reason.
    """
    q: mp.Queue = mp.Queue()
    p = mp.Process(target=_run_algorithm_in_process, args=(target_fn, g1, g2, q))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        p.join()
        return False, "timeout"

    try:
        status, payload = q.get_nowait()
    except Exception:
        return False, "no-result"

    if status == "ok":
        return True, payload
    return False, payload


def expand_edge_counts(n: int) -> List[int]:
    max_edges = n * (n - 1) // 2
    candidates = set()
    candidates.add(max(n - 1, 0))
    for m in EDGE_MULTIPLIERS:
        candidates.add(min(max_edges, int(n * m)))
    lst = sorted([c for c in candidates if c >= (n - 1)])
    return lst


def flatten_stats_row(base: Dict[str, Any], stats: Dict[str, Any]) -> Dict[str, Any]:
    row = dict(base)
    for k, v in (stats or {}).items():
        row[k] = v
    return row


def main():
    if RANDOM_SEED is not None:
        import random

        random.seed(RANDOM_SEED)

    algorithms = [
        ("bruteforce", compute_mces_bruteforce),
        ("bruteforce_arcmatch", compute_mces_bruteforce_arcmatch),
        ("connected_mces", compute_mces_connected),
        ("greedy_path_mces", compute_mces_greedy_path),
    ]

    # We'll write rows incrementally to CSV with a file lock to ensure consistency
    rows: List[Dict[str, Any]] = []

    total_runs = 0
    for n in range(N_MIN, N_MAX + 1):
        edge_counts = expand_edge_counts(n)
        for m in edge_counts:
            total_runs += REPEATS * len(algorithms)

    print(
        f"Benchmark plan: nodes {N_MIN}-{N_MAX}, repeats={REPEATS}, total runs ~ {total_runs}"
    )

    run_idx = 0

    # Prepare results directory and CSV file with header before running
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    results_dir = os.path.join(RESULTS_ROOT, timestamp)
    os.makedirs(results_dir, exist_ok=True)
    out_path = os.path.abspath(os.path.join(results_dir, OUTPUT_CSV))

    # Known/expected stat keys produced by algorithms (extendable)
    known_stat_keys = [
        "time_ms",
        "mappings_explored",
        "recursive_calls",
        "pruned_branches",
        "valid_edge_checks",
        "mces_size",
        "mapping_quality",
        "solution_optimality",
        "memory_usage_mb",
    ]

    preferred = [
        "algorithm",
        "num_nodes",
        "num_edges",
        "repeat",
        "timeout",
        "preserved_edges_count",
        "run_time_sec_wall",
    ]
    header = preferred + known_stat_keys

    # create CSV and write header
    with open(out_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=header)
        writer.writeheader()

    # helper to append a row with file-locking
    def append_row(row: Dict[str, Any]):
        # ensure consistent order and presence of keys
        out = {k: row.get(k, "") for k in header}
        with open(out_path, "a", newline="") as fh:
            # exclusive lock
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
                writer = csv.DictWriter(fh, fieldnames=header)
                writer.writerow(out)
                fh.flush()
                os.fsync(fh.fileno())
            finally:
                try:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
                except Exception:
                    pass

    # write metadata
    meta = {
        "generated_at": timestamp,
        "n_min": N_MIN,
        "n_max": N_MAX,
        "repeats": REPEATS,
        "edge_multipliers": EDGE_MULTIPLIERS,
        "per_call_timeout": PER_CALL_TIMEOUT,
        "random_seed": RANDOM_SEED,
    }
    try:
        import json

        with open(os.path.join(results_dir, "metadata.json"), "w") as mf:
            json.dump(meta, mf, indent=2)
    except Exception:
        pass
    # Use a ThreadPoolExecutor to submit algorithm runs concurrently (each run still
    # spawns a process internally to enforce timeouts). This avoids blocking the
    # main loop when a single algorithm is slow.
    futures = []
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    def run_and_record(alg_name, alg_fn, g1, g2, n, m, rep, idx, total):
        print(
            f"[{idx}/{total}] n={n} m={m} rep={rep} -> {alg_name} (timeout {PER_CALL_TIMEOUT}s)",
            end=" ",
        )
        started = time.time()
        finished, result = call_with_timeout(alg_fn, g1, g2, PER_CALL_TIMEOUT)
        elapsed = time.time() - started
        base = {
            "algorithm": alg_name,
            "num_nodes": n,
            "num_edges": m,
            "repeat": rep,
            "run_time_sec_wall": round(elapsed, 3),
        }

        if not finished:
            print("[TIMEOUT]")
            row = dict(base)
            row.update({"timeout": True})
            append_row(row)
            return

        print("[OK]")
        preserved = result.get("preserved_edges") if isinstance(result, dict) else None
        preserved_count = len(preserved) if preserved else 0
        stats = (result.get("stats") if isinstance(result, dict) else {}) or {}

        row = dict(base)
        row.update({"timeout": False, "preserved_edges_count": preserved_count})
        for k, v in stats.items():
            row[k] = v
        append_row(row)

    # Submit all runs to the threadpool
    for n in range(N_MIN, N_MAX + 1):
        edge_counts = expand_edge_counts(n)
        for m in edge_counts:
            for rep in range(1, REPEATS + 1):
                run_idx += 1
                g1, g2 = generate_random_graph_pair(num_nodes=n, num_edges=m)
                for alg_name, alg_fn in algorithms:
                    # capture current values in submission
                    futures.append(
                        executor.submit(
                            run_and_record,
                            alg_name,
                            alg_fn,
                            g1,
                            g2,
                            n,
                            m,
                            rep,
                            run_idx,
                            total_runs,
                        )
                    )

    # Wait for all tasks to finish
    for fut in as_completed(futures):
        try:
            fut.result()
        except Exception as e:
            print("Task failed:", e)

    executor.shutdown()
    print(f"Benchmark finished. Results written to {out_path}")


if __name__ == "__main__":
    main()
