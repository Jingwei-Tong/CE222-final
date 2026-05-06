"""Global DOF ordering for the heterosis Mindlin plate element (26 DOFs)."""

from __future__ import annotations

# Q8 serendipity order in mesh/core.py / shapes.q8_natural_nodes:
# 0 BL, 1 BR, 2 TR, 3 TL, 4 Bm, 5 Rm, 6 Tm, 7 Lm
SLICE_W = slice(0, 8)
# Q9 Lagrange: same eight + 9 interior center
SLICE_TX = slice(8, 17)
SLICE_TY = slice(17, 26)

NUM_DOF: int = 26
