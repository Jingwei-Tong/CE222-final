from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from assembly import build_dof_map
from config import ProblemConfig
from mesh import MeshSpec, generate_mesh
from post.point_queries import find_node_at_point, query_point_A_deflection, query_point_deflection
from solver.model_runner import run_model


class PointQueriesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ProblemConfig()
        self.mesh = generate_mesh(self.config, MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1))
        self.dof_map = build_dof_map(self.mesh)

    def test_find_node_at_point_returns_exact_node(self) -> None:
        point_a = self.config.point_A_coordinates
        node_id = find_node_at_point(self.mesh, point_a)
        self.assertIsNotNone(node_id)
        self.assertEqual(self.mesh.nodes[node_id], point_a)

    def test_point_query_returns_exact_nodal_value_when_applicable(self) -> None:
        solution = np.zeros(self.dof_map.num_dof)
        point_a = self.config.point_A_coordinates
        node_id = find_node_at_point(self.mesh, point_a)
        self.assertIsNotNone(node_id)
        solution[self.dof_map.w_dof(node_id)] = 12.345
        self.assertAlmostEqual(query_point_deflection(solution, self.mesh, point_a), 12.345)
        self.assertAlmostEqual(query_point_A_deflection(solution, self.mesh, self.config), 12.345)

    def test_non_nodal_query_raises(self) -> None:
        solution = np.zeros(self.dof_map.num_dof)
        with self.assertRaises(ValueError):
            query_point_deflection(solution, self.mesh, (10.0, 10.0))


class ModelRunnerPointAIntegrationTests(unittest.TestCase):
    def test_run_model_returns_point_a_deflection(self) -> None:
        result = run_model(ProblemConfig(applied_shear=1.0), MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1))
        self.assertTrue(np.isfinite(result.point_A_deflection))
        self.assertAlmostEqual(result.point_A_deflection, query_point_A_deflection(result.u_full, result.mesh, result.config))


if __name__ == "__main__":
    unittest.main()
