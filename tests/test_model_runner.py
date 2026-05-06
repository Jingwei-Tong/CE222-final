from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
from scipy import sparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import ProblemConfig
from mesh import MeshSpec
from solver.model_runner import run_model


class ModelRunnerTests(unittest.TestCase):
    def test_default_problem_setup_matches_assignment_interpretation(self) -> None:
        config = ProblemConfig()
        self.assertEqual(config.clamped_edges, ("left", "top"))
        self.assertEqual(config.free_edges, ("right", "bottom"))
        self.assertEqual(config.loaded_edges, ("hole_top",))

    def test_small_model_runs_without_failure(self) -> None:
        config = ProblemConfig(applied_shear=1.0)
        spec = MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1)
        result = run_model(config, spec)

        self.assertEqual(result.k_full.shape, (result.dof_map_num_dof, result.dof_map_num_dof))
        self.assertTrue(sparse.issparse(result.k_full))
        self.assertEqual(result.f_full.shape, (result.dof_map_num_dof,))
        self.assertEqual(result.u_full.shape, (result.dof_map_num_dof,))
        self.assertEqual(result.k_reduced.shape, (len(result.free_dofs), len(result.free_dofs)))
        self.assertTrue(sparse.issparse(result.k_reduced))
        self.assertLess(result.solve_result.residual_norm, 1e-8)

    def test_zero_load_gives_zero_solution(self) -> None:
        config = ProblemConfig(applied_shear=0.0)
        spec = MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1)
        result = run_model(config, spec)

        self.assertTrue(np.allclose(result.f_full, 0.0))
        self.assertTrue(np.allclose(result.u_full, 0.0))


if __name__ == "__main__":
    unittest.main()
