from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import ProblemConfig
from mesh import MeshSpec, generate_mesh
from mesh.visualization import (
    plot_boundary_edges,
    plot_boundary_nodes,
    plot_mesh,
    plot_patch_layout,
)


class VisualizationModuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ProblemConfig()
        self.mesh = generate_mesh(self.config, MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1))

    def test_plot_mesh_returns_figure_and_axes(self) -> None:
        fig, ax = plot_mesh(self.mesh, self.config)
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        fig.clf()

    def test_plot_patch_layout_returns_figure_and_axes(self) -> None:
        fig, ax = plot_patch_layout(self.mesh, self.config)
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        fig.clf()

    def test_boundary_plot_functions_run(self) -> None:
        fig1, ax1 = plot_boundary_nodes(self.mesh, self.config, "left")
        fig2, ax2 = plot_boundary_edges(self.mesh, self.config, "hole_top")
        self.assertIsNotNone(fig1)
        self.assertIsNotNone(ax1)
        self.assertIsNotNone(fig2)
        self.assertIsNotNone(ax2)
        fig1.clf()
        fig2.clf()

    def test_plot_mesh_can_save_png(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "mesh.png"
            fig, _ = plot_mesh(self.mesh, self.config, save_path=output_path)
            self.assertTrue(output_path.exists())
            fig.clf()


if __name__ == "__main__":
    unittest.main()
