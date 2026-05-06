from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from examples.final_plate_with_cutout import default_refinement_series, run_final_case


class FinalCaseExampleTests(unittest.TestCase):
    def test_default_refinement_series_is_nonempty(self) -> None:
        specs = default_refinement_series()
        self.assertGreaterEqual(len(specs), 1)

    def test_run_final_case_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            artifacts = run_final_case(tmp_dir)
            self.assertTrue(artifacts.table_path.exists())
            self.assertTrue(artifacts.plot_path.exists())
            self.assertTrue(artifacts.surface_plot_path.exists())
            self.assertTrue(artifacts.contour_plot_path.exists())
            self.assertTrue(artifacts.interactive_surface_path.exists())
            self.assertIn("w(A)", artifacts.convergence_table)


if __name__ == "__main__":
    unittest.main()
