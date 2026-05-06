from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from element.heterosis import heterosis_element_stiffness
from element.shapes import q8_natural_nodes, q8_shape, q9_natural_nodes, q9_shape


def _reproduce_field(n: np.ndarray, node_vals: np.ndarray) -> float:
    return float(np.dot(n, node_vals))


class Q8ShapeTests(unittest.TestCase):
    def test_partition_of_unity(self) -> None:
        for xi, eta in [(-0.7, 0.3), (0.0, 0.0), (0.6, -0.4)]:
            n, _ = q8_shape(xi, eta)
            self.assertAlmostEqual(float(np.sum(n)), 1.0, places=12)

    def test_linear_completeness(self) -> None:
        nodes = q8_natural_nodes()
        for xi, eta in [(-0.4, 0.5), (0.2, 0.2), (0.8, -0.6)]:
            n, _ = q8_shape(xi, eta)
            xi_hat = _reproduce_field(n, nodes[:, 0])
            eta_hat = _reproduce_field(n, nodes[:, 1])
            self.assertAlmostEqual(xi_hat, xi, places=10)
            self.assertAlmostEqual(eta_hat, eta, places=10)

    def test_nodal_interpolation(self) -> None:
        nodes = q8_natural_nodes()
        for k in range(8):
            xi, eta = float(nodes[k, 0]), float(nodes[k, 1])
            n, _ = q8_shape(xi, eta)
            for j in range(8):
                if j == k:
                    self.assertAlmostEqual(float(n[j]), 1.0, places=10)
                else:
                    self.assertAlmostEqual(float(n[j]), 0.0, places=10)


class Q9ShapeTests(unittest.TestCase):
    def test_partition_of_unity(self) -> None:
        for xi, eta in [(-0.7, 0.3), (0.0, 0.0), (0.6, -0.4)]:
            n, _ = q9_shape(xi, eta)
            self.assertAlmostEqual(float(np.sum(n)), 1.0, places=12)

    def test_linear_completeness(self) -> None:
        nodes = q9_natural_nodes()
        for xi, eta in [(-0.4, 0.5), (0.2, 0.2), (0.8, -0.6)]:
            n, _ = q9_shape(xi, eta)
            xi_hat = _reproduce_field(n, nodes[:, 0])
            eta_hat = _reproduce_field(n, nodes[:, 1])
            self.assertAlmostEqual(xi_hat, xi, places=10)
            self.assertAlmostEqual(eta_hat, eta, places=10)

    def test_quadratic_monomials(self) -> None:
        nodes = q9_natural_nodes()
        for xi, eta in [(-0.55, 0.45), (0.33, -0.22), (0.71, 0.61)]:
            n, _ = q9_shape(xi, eta)
            self.assertAlmostEqual(_reproduce_field(n, nodes[:, 0] ** 2), xi**2, places=9)
            self.assertAlmostEqual(_reproduce_field(n, nodes[:, 1] ** 2), eta**2, places=9)
            prod = nodes[:, 0] * nodes[:, 1]
            self.assertAlmostEqual(_reproduce_field(n, prod), xi * eta, places=9)

    def test_nodal_interpolation(self) -> None:
        nodes = q9_natural_nodes()
        for k in range(9):
            xi, eta = float(nodes[k, 0]), float(nodes[k, 1])
            n, _ = q9_shape(xi, eta)
            for j in range(9):
                if j == k:
                    self.assertAlmostEqual(float(n[j]), 1.0, places=10)
                else:
                    self.assertAlmostEqual(float(n[j]), 0.0, places=10)


class HeterosisStiffnessTests(unittest.TestCase):
    def test_stiffness_symmetric(self) -> None:
        xy = np.array(
            [
                [0.0, 0.0],
                [2.0, 0.0],
                [2.0, 1.0],
                [0.0, 1.0],
                [1.0, 0.0],
                [2.0, 0.5],
                [1.0, 1.0],
                [0.0, 0.5],
            ],
            dtype=float,
        )
        k = heterosis_element_stiffness(xy, young_modulus=200_000.0, poisson_ratio=0.25, thickness=20.0)
        self.assertEqual(k.shape, (26, 26))
        self.assertTrue(np.allclose(k, k.T, atol=1e-10))


if __name__ == "__main__":
    unittest.main()
