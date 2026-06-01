"""Safety/engine modules owned by person A."""

from .danger import compute_danger_map
from .masks import legal_actions, safe_actions
from .obs import parse_obs
from .shield import final_shield

__all__ = [
    "compute_danger_map",
    "final_shield",
    "legal_actions",
    "parse_obs",
    "safe_actions",
]
