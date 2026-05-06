from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import ProblemConfig


class ProblemConfigTests(unittest.TestCase):
    def test_default_cutout_is_centered(self) -> None:
        config = ProblemConfig()
        self.assertEqual(config.hole_x_min, 125.0)
        self.assertEqual(config.hole_x_max, 375.0)
        self.assertEqual(config.hole_y_min, 60.0)
        self.assertEqual(config.hole_y_max, 240.0)

    def test_default_young_modulus_matches_project_interpretation(self) -> None:
        config = ProblemConfig()
        self.assertEqual(config.young_modulus, 200.0)

    def test_default_point_A_uses_cutout_corner(self) -> None:
        config = ProblemConfig()
        self.assertEqual(config.point_A_coordinates, (375.0, 60.0))

    def test_custom_point_A_is_respected(self) -> None:
        config = ProblemConfig(point_A=(300.0, 120.0))
        self.assertEqual(config.point_A_coordinates, (300.0, 120.0))

    def test_invalid_edge_name_raises(self) -> None:
        with self.assertRaises(ValueError):
            ProblemConfig(clamped_edges=("north",))

    def test_invalid_loaded_edge_name_raises(self) -> None:
        with self.assertRaises(ValueError):
            ProblemConfig(loaded_edges=("north",))

    def test_edge_flags_cannot_overlap(self) -> None:
        with self.assertRaises(ValueError):
            ProblemConfig(clamped_edges=("left",), free_edges=("left", "top"))

    def test_cutout_must_fit_inside_plate(self) -> None:
        with self.assertRaises(ValueError):
            ProblemConfig(cutout_width=500.0)

    def test_young_modulus_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            ProblemConfig(young_modulus=0.0)

    def test_thickness_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            ProblemConfig(thickness=0.0)

    def test_poisson_ratio_must_be_valid(self) -> None:
        with self.assertRaises(ValueError):
            ProblemConfig(poisson_ratio=0.6)

    def test_point_A_must_stay_inside_plate(self) -> None:
        with self.assertRaises(ValueError):
            ProblemConfig(point_A=(999.0, 999.0))


if __name__ == "__main__":
    unittest.main()
