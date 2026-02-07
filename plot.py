#!/usr/bin/env python3
"""
Script to generate comparison plots from benchmark results.
Usage: python plot.py <path_to_csv_file>
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

# Configurazione stile grafici
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 8)
plt.rcParams["font.size"] = 10


def load_data(csv_path):
    """Load data from CSV file."""
    df = pd.read_csv(csv_path)
    return df


def get_output_dir(csv_path):
    """Determine output directory (graphs subfolder of CSV)."""
    graphs_dir = Path(csv_path).parent / "graphs"
    graphs_dir.mkdir(exist_ok=True)
    return graphs_dir


def plot_execution_time_comparison(df, output_dir):
    """Compare average execution times per algorithm."""
    plt.figure(figsize=(14, 8))

    # Group by algorithm and calculate statistics
    time_stats = df.groupby("algorithm")["time_ms"].agg(["mean", "std", "median"])
    time_stats = time_stats.sort_values("mean")

    # Bar plot with errors
    ax = plt.subplot(111)
    x = range(len(time_stats))
    ax.bar(
        x,
        time_stats["mean"],
        yerr=time_stats["std"],
        capsize=5,
        alpha=0.7,
        color="steelblue",
    )
    ax.set_xlabel("Algorithm", fontweight="bold")
    ax.set_ylabel("Average time (ms)", fontweight="bold")
    ax.set_title(
        "Average execution time comparison per algorithm",
        fontweight="bold",
        fontsize=14,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(time_stats.index, rotation=45, ha="right")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "execution_time_comparison.svg", format="svg", dpi=300)
    plt.close()
    print(f"Created: execution_time_comparison.svg")


def plot_execution_time_boxplot(df, output_dir):
    """Boxplot of execution times per algorithm."""
    plt.figure(figsize=(14, 8))

    # Sort algorithms by median time
    order = df.groupby("algorithm")["time_ms"].median().sort_values().index

    ax = sns.boxplot(
        data=df,
        x="algorithm",
        y="time_ms",
        order=order,
        hue="algorithm",
        palette="Set2",
        legend=False,
    )
    ax.set_xlabel("Algorithm", fontweight="bold")
    ax.set_ylabel("Execution time (ms)", fontweight="bold")
    ax.set_title(
        "Execution time distribution per algorithm", fontweight="bold", fontsize=14
    )
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "execution_time_boxplot.svg", format="svg", dpi=300)
    plt.close()
    print(f"Created: execution_time_boxplot.svg")


def plot_memory_usage_comparison(df, output_dir):
    """Compare memory usage per algorithm."""
    plt.figure(figsize=(14, 8))

    memory_stats = df.groupby("algorithm")["memory_usage_mb"].agg(["mean", "std"])
    memory_stats = memory_stats.sort_values("mean")

    ax = plt.subplot(111)
    x = range(len(memory_stats))
    ax.bar(
        x,
        memory_stats["mean"],
        yerr=memory_stats["std"],
        capsize=5,
        alpha=0.7,
        color="coral",
    )
    ax.set_xlabel("Algorithm", fontweight="bold")
    ax.set_ylabel("Memory used (MB)", fontweight="bold")
    ax.set_title(
        "Average memory usage comparison per algorithm", fontweight="bold", fontsize=14
    )
    ax.set_xticks(x)
    ax.set_xticklabels(memory_stats.index, rotation=45, ha="right")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "memory_usage_comparison.svg", format="svg", dpi=300)
    plt.close()
    print(f"Created: memory_usage_comparison.svg")


def plot_solution_quality(df, output_dir):
    """Compare solution quality (preserved edges)."""
    plt.figure(figsize=(14, 8))

    quality_stats = df.groupby("algorithm")["preserved_edges_count"].agg(
        ["mean", "std"]
    )
    quality_stats = quality_stats.sort_values("mean", ascending=False)

    ax = plt.subplot(111)
    x = range(len(quality_stats))
    ax.bar(
        x,
        quality_stats["mean"],
        yerr=quality_stats["std"],
        capsize=5,
        alpha=0.7,
        color="seagreen",
    )
    ax.set_xlabel("Algorithm", fontweight="bold")
    ax.set_ylabel("Preserved edges (average)", fontweight="bold")
    ax.set_title(
        "Solution quality comparison: preserved edges", fontweight="bold", fontsize=14
    )
    ax.set_xticks(x)
    ax.set_xticklabels(quality_stats.index, rotation=45, ha="right")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "solution_quality.svg", format="svg", dpi=300)
    plt.close()
    print(f"Created: solution_quality.svg")


def plot_optimality_rate(df, output_dir):
    """Show optimality rate per algorithm."""
    plt.figure(figsize=(14, 8))

    # Calculate percentage of optimal solutions
    optimality = df.groupby("algorithm")["solution_optimality"].mean() * 100
    optimality = optimality.sort_values(ascending=False)

    ax = plt.subplot(111)
    colors = [
        "green" if v == 100 else "orange" if v >= 50 else "red"
        for v in optimality.values
    ]
    ax.bar(range(len(optimality)), optimality.values, alpha=0.7, color=colors)
    ax.set_xlabel("Algorithm", fontweight="bold")
    ax.set_ylabel("Optimal solutions (%)", fontweight="bold")
    ax.set_title("Solution optimality rate", fontweight="bold", fontsize=14)
    ax.set_xticks(range(len(optimality)))
    ax.set_xticklabels(optimality.index, rotation=45, ha="right")
    ax.set_ylim(0, 105)
    ax.axhline(y=100, color="green", linestyle="--", alpha=0.5, label="100% optimal")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()

    # Add values on bars
    for i, v in enumerate(optimality.values):
        ax.text(i, v + 2, f"{v:.1f}%", ha="center", va="bottom", fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_dir / "optimality_rate.svg", format="svg", dpi=300)
    plt.close()
    print(f"Created: optimality_rate.svg")


def plot_time_vs_graph_size(df, output_dir):
    """Execution time as a function of graph size."""
    plt.figure(figsize=(14, 8))

    algorithms = df["algorithm"].unique()
    colors = sns.color_palette("husl", len(algorithms))

    for algo, color in zip(algorithms, colors):
        algo_data = df[df["algorithm"] == algo]
        # Group by num_nodes and calculate average
        grouped = algo_data.groupby("num_nodes")["time_ms"].mean()
        plt.plot(
            grouped.index,
            grouped.values,
            marker="o",
            label=algo,
            linewidth=2,
            markersize=8,
            alpha=0.7,
            color=color,
        )

    plt.xlabel("Number of nodes", fontweight="bold")
    plt.ylabel("Average execution time (ms)", fontweight="bold")
    plt.title("Scalability: time vs graph size", fontweight="bold", fontsize=14)
    plt.legend(loc="best", framealpha=0.9)
    plt.grid(True, alpha=0.3)
    plt.yscale("log")

    plt.tight_layout()
    plt.savefig(output_dir / "time_vs_graph_size.svg", format="svg", dpi=300)
    plt.close()
    print(f"Created: time_vs_graph_size.svg")


def plot_time_vs_edges(df, output_dir):
    """Execution time as a function of number of edges."""
    plt.figure(figsize=(14, 8))

    algorithms = df["algorithm"].unique()
    colors = sns.color_palette("husl", len(algorithms))

    for algo, color in zip(algorithms, colors):
        algo_data = df[df["algorithm"] == algo]
        grouped = algo_data.groupby("num_edges")["time_ms"].mean()
        plt.plot(
            grouped.index,
            grouped.values,
            marker="s",
            label=algo,
            linewidth=2,
            markersize=8,
            alpha=0.7,
            color=color,
        )

    plt.xlabel("Number of edges", fontweight="bold")
    plt.ylabel("Average execution time (ms)", fontweight="bold")
    plt.title("Scalability: time vs number of edges", fontweight="bold", fontsize=14)
    plt.legend(loc="best", framealpha=0.9)
    plt.grid(True, alpha=0.3)
    plt.yscale("log")

    plt.tight_layout()
    plt.savefig(output_dir / "time_vs_edges.svg", format="svg", dpi=300)
    plt.close()
    print(f"Created: time_vs_edges.svg")


def plot_search_space_exploration(df, output_dir):
    """Compare explored search space."""
    plt.figure(figsize=(14, 8))

    # Filter algorithms that have mappings_explored data
    df_filtered = df[df["mappings_explored"].notna() & (df["mappings_explored"] > 0)]

    if len(df_filtered) > 0:
        exploration_stats = df_filtered.groupby("algorithm")["mappings_explored"].agg(
            ["mean", "std"]
        )
        exploration_stats = exploration_stats.sort_values("mean")

        ax = plt.subplot(111)
        x = range(len(exploration_stats))
        ax.bar(
            x,
            exploration_stats["mean"],
            yerr=exploration_stats["std"],
            capsize=5,
            alpha=0.7,
            color="mediumpurple",
        )
        ax.set_xlabel("Algorithm", fontweight="bold")
        ax.set_ylabel("Mappings explored (average)", fontweight="bold")
        ax.set_title(
            "Search space exploration comparison", fontweight="bold", fontsize=14
        )
        ax.set_xticks(x)
        ax.set_xticklabels(exploration_stats.index, rotation=45, ha="right")
        ax.set_yscale("log")
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_dir / "search_space_exploration.svg", format="svg", dpi=300)
        plt.close()
        print(f"Created: search_space_exploration.svg")
    else:
        print("⊘ Skipped: search_space_exploration.svg (data not available)")


def plot_recursive_calls(df, output_dir):
    """Compare number of recursive calls."""
    plt.figure(figsize=(14, 8))

    df_filtered = df[df["recursive_calls"].notna() & (df["recursive_calls"] > 0)]

    if len(df_filtered) > 0:
        calls_stats = df_filtered.groupby("algorithm")["recursive_calls"].agg(
            ["mean", "std", "max"]
        )
        calls_stats = calls_stats.sort_values("mean")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        # Plot 1: Average
        x = range(len(calls_stats))
        ax1.bar(
            x,
            calls_stats["mean"],
            yerr=calls_stats["std"],
            capsize=5,
            alpha=0.7,
            color="teal",
        )
        ax1.set_xlabel("Algorithm", fontweight="bold")
        ax1.set_ylabel("Recursive calls (average)", fontweight="bold")
        ax1.set_title("Average recursive calls", fontweight="bold", fontsize=12)
        ax1.set_xticks(x)
        ax1.set_xticklabels(calls_stats.index, rotation=45, ha="right")
        ax1.grid(axis="y", alpha=0.3)

        # Plot 2: Max
        ax2.bar(x, calls_stats["max"], alpha=0.7, color="darkred")
        ax2.set_xlabel("Algorithm", fontweight="bold")
        ax2.set_ylabel("Recursive calls (max)", fontweight="bold")
        ax2.set_title("Maximum recursive calls", fontweight="bold", fontsize=12)
        ax2.set_xticks(x)
        ax2.set_xticklabels(calls_stats.index, rotation=45, ha="right")
        ax2.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_dir / "recursive_calls.svg", format="svg", dpi=300)
        plt.close()
        print(f"Created: recursive_calls.svg")
    else:
        print("⊘ Skipped: recursive_calls.svg (data not available)")


def plot_pruned_branches(df, output_dir):
    """Compare number of pruned branches."""
    plt.figure(figsize=(14, 8))

    df_filtered = df[df["pruned_branches"].notna() & (df["pruned_branches"] > 0)]

    if len(df_filtered) > 0:
        pruned_stats = df_filtered.groupby("algorithm")["pruned_branches"].agg(
            ["mean", "std"]
        )
        pruned_stats = pruned_stats.sort_values("mean", ascending=False)

        ax = plt.subplot(111)
        x = range(len(pruned_stats))
        ax.bar(
            x,
            pruned_stats["mean"],
            yerr=pruned_stats["std"],
            capsize=5,
            alpha=0.7,
            color="indianred",
        )
        ax.set_xlabel("Algorithm", fontweight="bold")
        ax.set_ylabel("Pruned branches (average)", fontweight="bold")
        ax.set_title("Pruning effectiveness", fontweight="bold", fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(pruned_stats.index, rotation=45, ha="right")
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_dir / "pruned_branches.svg", format="svg", dpi=300)
        plt.close()
        print(f"Created: pruned_branches.svg")
    else:
        print("⊘ Skipped: pruned_branches.svg (data not available)")


def plot_efficiency_tradeoff(df, output_dir):
    """Scatter plot: time vs solution quality."""
    plt.figure(figsize=(14, 10))

    algorithms = df["algorithm"].unique()
    colors = sns.color_palette("husl", len(algorithms))

    for algo, color in zip(algorithms, colors):
        algo_data = df[df["algorithm"] == algo]
        plt.scatter(
            algo_data["time_ms"],
            algo_data["preserved_edges_count"],
            label=algo,
            alpha=0.6,
            s=100,
            color=color,
            edgecolors="black",
            linewidth=0.5,
        )

    plt.xlabel("Execution time (ms)", fontweight="bold")
    plt.ylabel("Preserved edges", fontweight="bold")
    plt.title(
        "Efficiency vs solution quality trade-off", fontweight="bold", fontsize=14
    )
    plt.legend(loc="best", framealpha=0.9)
    plt.grid(True, alpha=0.3)
    plt.xscale("log")

    plt.tight_layout()
    plt.savefig(output_dir / "efficiency_tradeoff.svg", format="svg", dpi=300)
    plt.close()
    print(f"Created: efficiency_tradeoff.svg")


def plot_timeout_analysis(df, output_dir):
    """Analyze timeouts per algorithm."""
    plt.figure(figsize=(14, 8))

    timeout_rate = df.groupby("algorithm")["timeout"].mean() * 100
    timeout_rate = timeout_rate.sort_values(ascending=False)

    ax = plt.subplot(111)
    colors = ["red" if v > 0 else "green" for v in timeout_rate.values]
    ax.bar(range(len(timeout_rate)), timeout_rate.values, alpha=0.7, color=colors)
    ax.set_xlabel("Algorithm", fontweight="bold")
    ax.set_ylabel("Timeout rate (%)", fontweight="bold")
    ax.set_title("Timeout rate per algorithm", fontweight="bold", fontsize=14)
    ax.set_xticks(range(len(timeout_rate)))
    ax.set_xticklabels(timeout_rate.index, rotation=45, ha="right")
    ax.grid(axis="y", alpha=0.3)

    # Add values on bars
    for i, v in enumerate(timeout_rate.values):
        if v > 0:
            ax.text(i, v + 1, f"{v:.1f}%", ha="center", va="bottom", fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_dir / "timeout_analysis.svg", format="svg", dpi=300)
    plt.close()
    print(f"Created: timeout_analysis.svg")


def plot_heatmap_time_by_size(df, output_dir):
    """Heatmap: average time per (algorithm, graph size)."""
    plt.figure(figsize=(14, 10))

    # Create pivot table
    pivot = df.pivot_table(
        values="time_ms", index="algorithm", columns="num_nodes", aggfunc="mean"
    )

    ax = sns.heatmap(
        pivot,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        cbar_kws={"label": "Average time (ms)"},
        linewidths=0.5,
    )
    ax.set_xlabel("Number of nodes", fontweight="bold")
    ax.set_ylabel("Algorithm", fontweight="bold")
    ax.set_title(
        "Heatmap: average time per algorithm and graph size",
        fontweight="bold",
        fontsize=14,
    )

    plt.tight_layout()
    plt.savefig(output_dir / "heatmap_time_by_size.svg", format="svg", dpi=300)
    plt.close()
    print(f"Created: heatmap_time_by_size.svg")


def plot_heatmap_quality_by_size(df, output_dir):
    """Heatmap: average quality per (algorithm, graph size)."""
    plt.figure(figsize=(14, 10))

    pivot = df.pivot_table(
        values="preserved_edges_count",
        index="algorithm",
        columns="num_nodes",
        aggfunc="mean",
    )

    ax = sns.heatmap(
        pivot,
        annot=True,
        fmt=".2f",
        cmap="YlGn",
        cbar_kws={"label": "Preserved edges (average)"},
        linewidths=0.5,
    )
    ax.set_xlabel("Number of nodes", fontweight="bold")
    ax.set_ylabel("Algorithm", fontweight="bold")
    ax.set_title(
        "Heatmap: solution quality per algorithm and graph size",
        fontweight="bold",
        fontsize=14,
    )

    plt.tight_layout()
    plt.savefig(output_dir / "heatmap_quality_by_size.svg", format="svg", dpi=300)
    plt.close()
    print(f"Created: heatmap_quality_by_size.svg")


def plot_statistical_comparison(df, output_dir):
    """Statistical comparison between algorithms (violin plot)."""
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))

    # Execution time
    order = df.groupby("algorithm")["time_ms"].median().sort_values().index
    sns.violinplot(
        data=df,
        x="algorithm",
        y="time_ms",
        order=order,
        ax=axes[0, 0],
        hue="algorithm",
        palette="muted",
        legend=False,
    )
    axes[0, 0].set_title("Execution time distribution", fontweight="bold")
    axes[0, 0].set_xlabel("Algorithm", fontweight="bold")
    axes[0, 0].set_ylabel("Time (ms)", fontweight="bold")
    axes[0, 0].tick_params(axis="x", rotation=45)
    axes[0, 0].set_yscale("log")

    # Memory
    order = df.groupby("algorithm")["memory_usage_mb"].median().sort_values().index
    sns.violinplot(
        data=df,
        x="algorithm",
        y="memory_usage_mb",
        order=order,
        ax=axes[0, 1],
        hue="algorithm",
        palette="muted",
        legend=False,
    )
    axes[0, 1].set_title("Memory usage distribution", fontweight="bold")
    axes[0, 1].set_xlabel("Algorithm", fontweight="bold")
    axes[0, 1].set_ylabel("Memory (MB)", fontweight="bold")
    axes[0, 1].tick_params(axis="x", rotation=45)

    # Solution quality
    order = (
        df.groupby("algorithm")["preserved_edges_count"]
        .median()
        .sort_values(ascending=False)
        .index
    )
    sns.violinplot(
        data=df,
        x="algorithm",
        y="preserved_edges_count",
        order=order,
        ax=axes[1, 0],
        hue="algorithm",
        palette="muted",
        legend=False,
    )
    axes[1, 0].set_title("Solution quality distribution", fontweight="bold")
    axes[1, 0].set_xlabel("Algorithm", fontweight="bold")
    axes[1, 0].set_ylabel("Preserved edges", fontweight="bold")
    axes[1, 0].tick_params(axis="x", rotation=45)

    # Optimality
    optimality = df.groupby("algorithm")["solution_optimality"].mean() * 100
    optimality = optimality.sort_values(ascending=False)
    axes[1, 1].bar(
        range(len(optimality)), optimality.values, alpha=0.7, color="skyblue"
    )
    axes[1, 1].set_title("Optimality rate", fontweight="bold")
    axes[1, 1].set_xlabel("Algorithm", fontweight="bold")
    axes[1, 1].set_ylabel("Optimality (%)", fontweight="bold")
    axes[1, 1].set_xticks(range(len(optimality)))
    axes[1, 1].set_xticklabels(optimality.index, rotation=45, ha="right")
    axes[1, 1].set_ylim(0, 105)

    plt.tight_layout()
    plt.savefig(output_dir / "statistical_comparison.svg", format="svg", dpi=300)
    plt.close()
    print(f"Created: statistical_comparison.svg")


def plot_performance_summary(df, output_dir):
    """Summary plot of normalized performance."""
    plt.figure(figsize=(14, 10))

    # Calculate normalized metrics (0-1, where 1 is better)
    algorithms = df["algorithm"].unique()
    metrics = {}

    for algo in algorithms:
        algo_data = df[df["algorithm"] == algo]

        # Time: lower is better (invert)
        time_mean = algo_data["time_ms"].mean()
        time_score = 1 / (1 + time_mean / df["time_ms"].mean())

        # Memory: lower is better (invert)
        mem_mean = algo_data["memory_usage_mb"].mean()
        mem_score = 1 / (1 + mem_mean / df["memory_usage_mb"].mean())

        # Optimality: higher is better
        optimality_score = algo_data["solution_optimality"].mean()

        metrics[algo] = {
            "Speed": time_score,
            "Memory efficiency": mem_score,
            "Optimality": optimality_score,
        }

    # Create DataFrame for plotting
    metrics_df = pd.DataFrame(metrics).T

    # Grouped bar chart
    x = np.arange(len(algorithms))
    width = 0.2

    fig, ax = plt.subplots(figsize=(16, 8))

    for i, metric in enumerate(metrics_df.columns):
        offset = width * (i - len(metrics_df.columns) / 2 + 0.5)
        ax.bar(x + offset, metrics_df[metric], width, label=metric, alpha=0.8)

    ax.set_xlabel("Algorithm", fontweight="bold")
    ax.set_ylabel("Normalized score (0-1)", fontweight="bold")
    ax.set_title("Normalized performance comparison", fontweight="bold", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms, rotation=45, ha="right")
    ax.legend(loc="best", framealpha=0.9)
    ax.set_ylim(0, 1.1)
    ax.grid(axis="y", alpha=0.3)
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_dir / "performance_summary.svg", format="svg", dpi=300)
    plt.close()
    print(f"Created: performance_summary.svg")


def plot_convergence_by_repeat(df, output_dir):
    """Analyze convergence by number of repetitions."""
    plt.figure(figsize=(14, 8))

    algorithms = df["algorithm"].unique()
    colors = sns.color_palette("husl", len(algorithms))

    for algo, color in zip(algorithms, colors):
        algo_data = df[df["algorithm"] == algo]
        grouped = algo_data.groupby("repeat")["time_ms"].mean()
        plt.plot(
            grouped.index,
            grouped.values,
            marker="o",
            label=algo,
            linewidth=2,
            markersize=8,
            alpha=0.7,
            color=color,
        )

    plt.xlabel("Repetition", fontweight="bold")
    plt.ylabel("Average time (ms)", fontweight="bold")
    plt.title("Stability: time per repetition", fontweight="bold", fontsize=14)
    plt.legend(loc="best", framealpha=0.9)
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "convergence_by_repeat.svg", format="svg", dpi=300)
    plt.close()
    print(f"Created: convergence_by_repeat.svg")


def generate_summary_statistics(df, output_dir):
    """Generate a text file with summary statistics."""
    summary_file = output_dir / "summary_statistics.txt"

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(" BENCHMARK SUMMARY STATISTICS\n")
        f.write("=" * 80 + "\n\n")

        # General information
        f.write(f"Total executions: {len(df)}\n")
        f.write(f"Algorithms tested: {df['algorithm'].nunique()}\n")
        f.write(f"  - {', '.join(df['algorithm'].unique())}\n\n")

        f.write(f"Graph size range:\n")
        f.write(f"  - Nodes: {df['num_nodes'].min()} - {df['num_nodes'].max()}\n")
        f.write(f"  - Edges: {df['num_edges'].min()} - {df['num_edges'].max()}\n\n")

        # Statistics per algorithm
        f.write("=" * 80 + "\n")
        f.write(" STATISTICS PER ALGORITHM\n")
        f.write("=" * 80 + "\n\n")

        for algo in sorted(df["algorithm"].unique()):
            algo_data = df[df["algorithm"] == algo]
            f.write(f"\n{algo.upper()}\n")
            f.write("-" * 80 + "\n")

            f.write(f"Executions: {len(algo_data)}\n")
            f.write(f"\nExecution time (ms):\n")
            f.write(f"  Mean: {algo_data['time_ms'].mean():.2f}\n")
            f.write(f"  Median: {algo_data['time_ms'].median():.2f}\n")
            f.write(f"  Std dev: {algo_data['time_ms'].std():.2f}\n")
            f.write(f"  Min: {algo_data['time_ms'].min():.2f}\n")
            f.write(f"  Max: {algo_data['time_ms'].max():.2f}\n")

            f.write(f"\nMemory (MB):\n")
            f.write(f"  Mean: {algo_data['memory_usage_mb'].mean():.2f}\n")
            f.write(f"  Std dev: {algo_data['memory_usage_mb'].std():.2f}\n")

            f.write(f"\nSolution quality:\n")
            f.write(
                f"  Preserved edges (average): {algo_data['preserved_edges_count'].mean():.2f}\n"
            )
            f.write(
                f"  Optimal solutions: {algo_data['solution_optimality'].sum()}/{len(algo_data)} "
            )
            f.write(f"({algo_data['solution_optimality'].mean()*100:.1f}%)\n")

            if algo_data["timeout"].sum() > 0:
                f.write(f"\n⚠ Timeout: {algo_data['timeout'].sum()} executions\n")

            if algo_data["mappings_explored"].notna().any():
                explored = algo_data["mappings_explored"].dropna()
                if len(explored) > 0:
                    f.write(f"\nSearch space:\n")
                    f.write(f"  Mappings explored (average): {explored.mean():.0f}\n")

            if algo_data["recursive_calls"].notna().any():
                calls = algo_data["recursive_calls"].dropna()
                if len(calls) > 0:
                    f.write(f"  Recursive calls (average): {calls.mean():.0f}\n")

            if algo_data["pruned_branches"].notna().any():
                pruned = algo_data["pruned_branches"].dropna()
                if len(pruned) > 0:
                    f.write(f"  Pruned branches (average): {pruned.mean():.0f}\n")

            f.write("\n")

        # Direct comparison
        f.write("\n" + "=" * 80 + "\n")
        f.write(" DIRECT COMPARISON\n")
        f.write("=" * 80 + "\n\n")

        f.write("Fastest algorithm (average time):\n")
        fastest = df.groupby("algorithm")["time_ms"].mean().idxmin()
        f.write(
            f"  🏆 {fastest}: {df[df['algorithm']==fastest]['time_ms'].mean():.2f} ms\n\n"
        )

        f.write("Best quality algorithm (preserved edges):\n")
        best_quality = df.groupby("algorithm")["preserved_edges_count"].mean().idxmax()
        f.write(
            f"  🏆 {best_quality}: {df[df['algorithm']==best_quality]['preserved_edges_count'].mean():.2f} edges\n\n"
        )

        f.write("Most memory efficient algorithm:\n")
        least_memory = df.groupby("algorithm")["memory_usage_mb"].mean().idxmin()
        f.write(
            f"  🏆 {least_memory}: {df[df['algorithm']==least_memory]['memory_usage_mb'].mean():.2f} MB\n\n"
        )

        f.write("Most reliable algorithm (% optimal solutions):\n")
        most_optimal = df.groupby("algorithm")["solution_optimality"].mean().idxmax()
        optimal_rate = (
            df[df["algorithm"] == most_optimal]["solution_optimality"].mean() * 100
        )
        f.write(f"  🏆 {most_optimal}: {optimal_rate:.1f}%\n\n")

    print(f"Created: summary_statistics.txt")


def main():
    parser = argparse.ArgumentParser(
        description="Generate comparison plots from MCES benchmark results"
    )
    parser.add_argument("csv_path", help="Path to the CSV file with results")

    args = parser.parse_args()
    csv_path = Path(args.csv_path)

    if not csv_path.exists():
        print(f"❌ Error: file {csv_path} not found!")
        return 1

    print(f"\n{'='*80}")
    print(f"  Generating plots from: {csv_path.name}")
    print(f"  Output directory: {csv_path.parent}/graphs")
    print(f"{'='*80}\n")

    # Load data
    print("📊 Loading data...")
    df = load_data(csv_path)
    output_dir = get_output_dir(csv_path)
    print(f"   Dataset: {len(df)} rows, {len(df['algorithm'].unique())} algorithms\n")

    # Generate all plots
    print("🎨 Generating plots...\n")

    plot_execution_time_comparison(df, output_dir)
    plot_execution_time_boxplot(df, output_dir)
    plot_memory_usage_comparison(df, output_dir)
    plot_solution_quality(df, output_dir)
    plot_optimality_rate(df, output_dir)
    plot_time_vs_graph_size(df, output_dir)
    plot_time_vs_edges(df, output_dir)
    plot_search_space_exploration(df, output_dir)
    plot_recursive_calls(df, output_dir)
    plot_pruned_branches(df, output_dir)
    plot_efficiency_tradeoff(df, output_dir)
    plot_timeout_analysis(df, output_dir)
    plot_heatmap_time_by_size(df, output_dir)
    plot_heatmap_quality_by_size(df, output_dir)
    plot_statistical_comparison(df, output_dir)
    plot_performance_summary(df, output_dir)
    plot_convergence_by_repeat(df, output_dir)

    # Generate text statistics
    print("\n📝 Generating statistics...\n")
    generate_summary_statistics(df, output_dir)

    print(f"\n{'='*80}")
    print(f"  ✅ Complete! All plots have been saved in:")
    print(f"     {output_dir}")
    print(f"{'='*80}\n")

    return 0


if __name__ == "__main__":
    exit(main())
