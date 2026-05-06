from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".mplconfig"))

from config import ProblemConfig
import element.heterosis as heterosis
import element.quadrature as quadrature
from mesh import MeshSpec
from solver.model_runner import run_model


class ShearLockingChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Keep the mesh modest so the diagnostic test stays fast.
        cls.spec = MeshSpec(nx_side=6, nx_hole=6, ny_side=6, ny_hole=6)

    def _point_a_deflection(self, thickness: float) -> float:
        result = run_model(ProblemConfig(thickness=thickness), self.spec)
        return float(result.point_A_deflection)

    def test_deflection_scales_close_to_inverse_thickness_cubed(self) -> None:
        values = {t: self._point_a_deflection(t) for t in (20.0, 10.0, 5.0)}
        scaled = np.array([abs(values[t]) * t**3 for t in (20.0, 10.0, 5.0)], dtype=float)

        # For bending-dominated behavior without severe locking, w * t^3 should stay
        # roughly constant as the plate gets thinner.
        ratio = float(np.max(scaled) / np.min(scaled))
        self.assertLess(ratio, 1.2)

    def test_full_shear_integration_does_not_show_large_extra_stiffening(self) -> None:
        selective = abs(self._point_a_deflection(5.0))

        original_gauss_2x2 = heterosis.gauss_2x2
        heterosis.gauss_2x2 = quadrature.gauss_3x3
        try:
            full_integration = abs(self._point_a_deflection(5.0))
        finally:
            heterosis.gauss_2x2 = original_gauss_2x2

        relative_difference = abs(full_integration - selective) / selective
        self.assertLess(relative_difference, 0.05)


if __name__ == "__main__":
    unittest.main()
