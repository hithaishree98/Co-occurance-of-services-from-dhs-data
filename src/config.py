"""
Shared Phase 1 constants.

Imported by src/phase1_matrix.py and src/phase1_heatmaps.py. Both are run as
`python src/<script>.py` from the repo root, which puts src/ on sys.path[0], so a
plain `from config import ...` resolves.

Deliberately holds no paths. The Phase 0 notebook runs from the repo root and would
need sys.path surgery to import this; keeping it script-only avoids that, and avoids
the src/__init__.py route (which would break the scripts, since src/ on sys.path[0]
means `src.config` is not importable from there).
"""

# Minimum shared-person count before a service pair is reported (M6).
# PROVISIONAL: a recorded choice, not a documented number. The county suppresses
# public cells under 6; 30 is deliberately more conservative. Revisit once Phase 1
# output shows how many pairs it excludes.
MIN_SUPPORT = 30
