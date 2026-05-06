from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from assembly import assemble_global_load, build_dof_map
from config import ProblemConfig
from mesh import MeshSpec, generate_mesh


class LoadVectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mesh = generate_mesh(ProblemConfig(), MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1))
        self.dof_map = build_dof_map(self.mesh)

    def test_top_only_load_matches_total_edge_force(self) -> None:
        config = ProblemConfig(applied_shear=2.5, loaded_edges=("top",))
        f = assemble_global_load(self.mesh, self.dof_map, config)
        self.assertAlmostEqual(float(np.sum(f[: self.dof_map.num_w_dof])), config.applied_shear * config.outer_width, places=10)
        self.assertAlmostEqual(float(np.sum(f[self.dof_map.num_w_dof :])), 0.0, places=12)

    def test_bottom_only_load_matches_total_edge_force_with_negative_sign(self) -> None:
        config = ProblemConfig(applied_shear=2.5, loaded_edges=("bottom",))
        f = assemble_global_load(self.mesh, self.dof_map, config)
        self.assertAlmostEqual(float(np.sum(f[: self.dof_map.num_w_dof])), -config.applied_shear * config.outer_width, places=10)
        self.assertAlmostEqual(float(np.sum(f[self.dof_map.num_w_dof :])), 0.0, places=12)

    def test_opposite_top_bottom_loads_cancel_in_total(self) -> None:
        config = ProblemConfig(applied_shear=1.75, loaded_edges=("top", "bottom"))
        f = assemble_global_load(self.mesh, self.dof_map, config)
        self.assertAlmostEqual(float(np.sum(f[: self.dof_map.num_w_dof])), 0.0, places=10)
        self.assertGreater(np.linalg.norm(f[: self.dof_map.num_w_dof]), 0.0)

    def test_hole_top_load_matches_cutout_width_force(self) -> None:
        config = ProblemConfig(applied_shear=3.0, loaded_edges=("hole_top",))
        f = assemble_global_load(self.mesh, self.dof_map, config)
        self.assertAlmostEqual(float(np.sum(f[: self.dof_map.num_w_dof])), -config.applied_shear * config.cutout_width, places=10)

    def test_unsupported_loaded_edge_raises(self) -> None:
        config = ProblemConfig(applied_shear=1.0, loaded_edges=("hole_left",))
        with self.assertRaises(ValueError):
            assemble_global_load(self.mesh, self.dof_map, config)


if __name__ == "__main__":
    unittest.main()
