"""Loadable folder agent for the Team A/B scaffold."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from .agent import Agent

__all__ = ["Agent"]
