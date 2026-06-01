"""Shared path setup so tests can import `person_a_safety` / `person_b_strategy`
as top-level packages (the same way the submitted agent is loaded) and also the
real `engine` package for the cross-validation harness.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TEAM_DIR = ROOT / "agent" / "team_agent"
SMOKE_DIR = Path(__file__).resolve().parent  # so sibling helpers import flat

for path in (ROOT, TEAM_DIR, SMOKE_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
