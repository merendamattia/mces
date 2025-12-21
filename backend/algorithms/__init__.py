"""Algorithm package for MCES prototypes.

Exports brute-force baselines; future algorithms can be added here.
"""

from .brute_force import compute_mces as compute_mces_bruteforce
from .brute_force_arcmatch import compute_mces as compute_mces_bruteforce_arcmatch

__all__ = [
    "compute_mces_bruteforce",
    "compute_mces_bruteforce_arcmatch",
]
