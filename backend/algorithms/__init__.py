"""Algorithm package for MCES prototypes.

Exports brute-force baselines; future algorithms can be added here.
"""

from .brute_force import compute_mces as compute_mces_bruteforce
from .brute_force_arcmatch import compute_mces as compute_mces_bruteforce_arcmatch
from .connected_mces import compute_mces_connected
from .greedy_path_mces import compute_mces_greedy_path

__all__ = [
    "compute_mces_bruteforce",
    "compute_mces_bruteforce_arcmatch",
    "compute_mces_connected",
    "compute_mces_greedy_path",
]
