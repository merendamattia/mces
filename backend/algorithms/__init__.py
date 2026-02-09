"""Algorithm package for MCES prototypes.

Exports brute-force baselines; future algorithms can be added here.
"""

from .brute_force import compute_mces as compute_mces_bruteforce
from .brute_force_pruning import compute_mces as compute_mces_bruteforce_pruning
from .connected_mces import compute_mces_connected
from .greedy_path_mces import compute_mces_greedy_path
from .ilp_r2 import compute_mces_ilp_r2
from .simulated_annealing_mces import compute_mces_simulated_annealing

__all__ = [
    "compute_mces_bruteforce",
    "compute_mces_bruteforce_pruning",
    "compute_mces_connected",
    "compute_mces_greedy_path",
    "compute_mces_ilp_r2",
    "compute_mces_simulated_annealing",
]
