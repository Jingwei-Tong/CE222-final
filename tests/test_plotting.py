from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import ProblemConfig
from mesh import MeshSpec
from post import (
    plot_convergence_deflection,
    plot_deflection_contour,
    plot_deflection_surface_3d,
    run_convergence_series,
    write_interactive_deflection_surface_html,
)
from solver.model_runner import run_model


class PlottingTests(unittest.TestCase):
    def test_plot_convergence_deflection_can_save_png(self) -> None:
        config = ProblemConfig(applied_shear=1.0)
        series = run_convergence_series(
            config,
            (
                MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1),
                MeshSpec(nx_side=2, nx_hole=2, ny_side=2, ny_hole=2),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "convergence.png"
            fig, ax = plot_convergence_deflection(series, save_path=path)
            self.assertEqual(ax.get_title(), "Convergence of Point A Deflection")
            self.assertTrue(path.exists())
            fig.clf()

    def test_plot_deflection_surface_3d_can_save_png(self) -> None:
        result = run_model(ProblemConfig(applied_shear=1.0), MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1))
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "surface3d.png"
            fig, ax = plot_deflection_surface_3d(result, save_path=path)
            self.assertIn("3D Deflection Surface", ax.get_title())
            self.assertTrue(path.exists())
            fig.clf()

    def test_plot_deflection_contour_can_save_png(self) -> None:
        result = run_model(ProblemConfig(applied_shear=1.0), MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1))
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "contour.png"
            fig, ax = plot_deflection_contour(result, save_path=path)
            self.assertEqual(ax.get_title(), "Deflection Contour")
            self.assertTrue(path.exists())
            fig.clf()

    def test_write_interactive_deflection_surface_html(self) -> None:
        result = run_model(ProblemConfig(applied_shear=1.0), MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1))
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "surface.html"
            out = write_interactive_deflection_surface_html(result, path)
            self.assertEqual(out, path)
            self.assertTrue(path.exists())
            self.assertIn("Plotly.newPlot", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
