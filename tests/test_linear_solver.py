from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
from scipy import sparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from solver.linear_solver import solve_system


class LinearSolverTests(unittest.TestCase):
    def test_known_small_system_solves_correctly(self) -> None:
        k = np.array([[4.0, 1.0], [1.0, 3.0]])
        f = np.array([1.0, 2.0])
        result = solve_system(k, f)
        expected = np.linalg.solve(k, f)
        self.assertTrue(np.allclose(result.u_free, expected))
        self.assertLess(result.residual_norm, 1e-12)

    def test_zero_size_system_raises(self) -> None:
        with self.assertRaises(ValueError):
            solve_system(np.zeros((0, 0)), np.zeros(0))

    def test_dimension_mismatch_raises(self) -> None:
        with self.assertRaises(ValueError):
            solve_system(np.eye(2), np.ones(3))

    def test_singular_system_raises(self) -> None:
        with self.assertRaises(np.linalg.LinAlgError):
            solve_system(np.array([[1.0, 1.0], [1.0, 1.0]]), np.array([1.0, 1.0]))

    def test_known_small_sparse_system_solves_correctly(self) -> None:
        k = sparse.csr_matrix(np.array([[4.0, 1.0], [1.0, 3.0]]))
        f = np.array([1.0, 2.0])
        result = solve_system(k, f)
        expected = np.linalg.solve(k.toarray(), f)
        self.assertTrue(np.allclose(result.u_free, expected))
        self.assertLess(result.residual_norm, 1e-12)


if __name__ == "__main__":
    unittest.main()
