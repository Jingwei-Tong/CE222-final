from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
from scipy import sparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from assembly import apply_clamped_bc, build_dof_map, clamped_dofs, expand_solution
from config import ProblemConfig
from mesh import MeshSpec, generate_mesh


class BoundaryConditionsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ProblemConfig()
        self.mesh = generate_mesh(self.config, MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1))
        self.dof_map = build_dof_map(self.mesh)

    def test_clamped_dofs_cover_all_three_dofs_on_left_and_top(self) -> None:
        constrained = clamped_dofs(self.mesh, self.dof_map, self.config)
        expected_nodes = set(self.mesh.boundary_nodes["left"]) | set(self.mesh.boundary_nodes["top"])
        self.assertEqual(len(constrained), 3 * len(expected_nodes))
        for node_id in expected_nodes:
            self.assertIn(self.dof_map.w_dof(node_id), constrained)
            self.assertIn(self.dof_map.tx_dof(node_id), constrained)
            self.assertIn(self.dof_map.ty_dof(node_id), constrained)

    def test_apply_clamped_bc_returns_disjoint_free_and_constrained_sets(self) -> None:
        constrained = clamped_dofs(self.mesh, self.dof_map, self.config)
        k_full = sparse.eye(self.dof_map.num_dof, format="csr")
        f_full = np.arange(self.dof_map.num_dof, dtype=float)
        k_reduced, f_reduced, free_dofs = apply_clamped_bc(k_full, f_full, constrained)
        self.assertEqual(len(np.intersect1d(free_dofs, constrained)), 0)
        self.assertEqual(k_reduced.shape, (len(free_dofs), len(free_dofs)))
        self.assertEqual(f_reduced.shape, (len(free_dofs),))

    def test_expand_solution_reconstructs_full_vector(self) -> None:
        free_dofs = np.array([1, 3, 5], dtype=int)
        u_free = np.array([10.0, 20.0, 30.0])
        u_full = expand_solution(u_free, free_dofs, total_dof=7)
        self.assertTrue(np.allclose(u_full, [0.0, 10.0, 0.0, 20.0, 0.0, 30.0, 0.0]))


if __name__ == "__main__":
    unittest.main()
