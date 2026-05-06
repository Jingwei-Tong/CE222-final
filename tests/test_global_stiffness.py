from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
from scipy import sparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from assembly import assemble_global_stiffness, build_dof_map, element_q8_coordinates
from config import ProblemConfig
from mesh import MeshSpec, generate_mesh


class GlobalStiffnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ProblemConfig()
        self.mesh = generate_mesh(self.config, MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1))
        self.dof_map = build_dof_map(self.mesh)

    def test_element_q8_coordinates_shape(self) -> None:
        xy_q8 = element_q8_coordinates(self.mesh, self.mesh.elements[0])
        self.assertEqual(xy_q8.shape, (8, 2))

    def test_global_stiffness_has_expected_shape(self) -> None:
        k = assemble_global_stiffness(self.mesh, self.dof_map, self.config)
        self.assertEqual(k.shape, (self.dof_map.num_dof, self.dof_map.num_dof))

    def test_global_stiffness_is_symmetric_and_nonzero(self) -> None:
        k = assemble_global_stiffness(self.mesh, self.dof_map, self.config)
        self.assertTrue(sparse.issparse(k))
        symmetry_error = k - k.T
        self.assertEqual(symmetry_error.nnz, 0)
        self.assertGreater(float(np.max(np.abs(k.data))), 0.0)
        self.assertGreater(k.nnz, 0)


if __name__ == "__main__":
    unittest.main()
