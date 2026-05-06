from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import ProblemConfig
from mesh import MeshSpec
from post.convergence import format_convergence_table, run_convergence_series


class ConvergenceTests(unittest.TestCase):
    def test_run_convergence_series_returns_rows(self) -> None:
        config = ProblemConfig(applied_shear=1.0)
        specs = (
            MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1),
            MeshSpec(nx_side=2, nx_hole=2, ny_side=2, ny_hole=2),
        )
        series = run_convergence_series(config, specs)

        self.assertEqual(len(series.rows), 2)
        self.assertLess(series.rows[0].num_nodes, series.rows[1].num_nodes)
        self.assertLess(series.rows[0].num_elements, series.rows[1].num_elements)
        self.assertLess(series.rows[0].num_dof, series.rows[1].num_dof)
        self.assertTrue(all(np.isfinite(row.point_A_deflection) for row in series.rows))

    def test_format_convergence_table_contains_headers_and_labels(self) -> None:
        config = ProblemConfig(applied_shear=0.0)
        specs = (MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1),)
        series = run_convergence_series(config, specs)
        table = format_convergence_table(series)

        self.assertIn("label", table)
        self.assertIn("nodes", table)
        self.assertIn("w(A)", table)
        self.assertIn(series.rows[0].label, table)

    def test_empty_refinement_list_raises(self) -> None:
        with self.assertRaises(ValueError):
            run_convergence_series(ProblemConfig(), [])


if __name__ == "__main__":
    unittest.main()
