"""Unit tests for element/quadrature, constitutive, jacobian, and stiffness consistency."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from element.b_matrix import bending_B_matrix, shear_B_matrix
from element.constitutive import mindlin_bending_matrix, mindlin_shear_matrix
from element.dofs import NUM_DOF
from element.heterosis import heterosis_element_stiffness
from element.jacobian import physical_derivatives_q8, physical_derivatives_q9, q8_jacobian
from element.quadrature import gauss_1d, gauss_2x2, gauss_3x3, gauss_tensor_2d


class QuadratureTests(unittest.TestCase):
    def test_2x2_weights_sum_to_reference_area(self) -> None:
        total = sum(gp.weight for gp in gauss_2x2())
        self.assertAlmostEqual(total, 4.0, places=14)

    def test_3x3_weights_sum_to_reference_area(self) -> None:
        total = sum(gp.weight for gp in gauss_3x3())
        self.assertAlmostEqual(total, 4.0, places=14)

    def test_3x3_exact_for_xi_squared_times_constant_eta(self) -> None:
        # int_{-1}^{1} int_{-1}^{1} xi^2 deta dxi = (2/3) * 2 = 4/3
        s = sum(gp.weight * gp.xi**2 for gp in gauss_3x3())
        self.assertAlmostEqual(s, 4.0 / 3.0, places=12)

    def test_1d_weights_sum_to_two(self) -> None:
        for order in (2, 3):
            pts = gauss_1d(order)
            self.assertAlmostEqual(sum(w for _, w in pts), 2.0, places=14)

    def test_unsupported_gauss_order_raises(self) -> None:
        with self.assertRaises(ValueError):
            gauss_1d(1)
        with self.assertRaises(ValueError):
            gauss_tensor_2d(1)


class ConstitutiveTests(unittest.TestCase):
    def test_bending_matrix_symmetric_positive_definite(self) -> None:
        d = mindlin_bending_matrix(210_000.0, 0.3, 12.0)
        self.assertEqual(d.shape, (3, 3))
        self.assertTrue(np.allclose(d, d.T))
        eig = np.linalg.eigvalsh(d)
        self.assertTrue(np.all(eig > 0.0))

    def test_shear_matrix_isotropic_scaling(self) -> None:
        d = mindlin_shear_matrix(200_000.0, 0.25, 20.0, shear_correction=5.0 / 6.0)
        self.assertEqual(d.shape, (2, 2))
        self.assertTrue(np.allclose(d, d.T))
        g = 200_000.0 / (2.0 * (1.0 + 0.25))
        kappa = (5.0 / 6.0) * g * 20.0
        self.assertAlmostEqual(float(d[0, 0]), kappa, places=10)
        self.assertAlmostEqual(float(d[1, 1]), kappa, places=10)
        self.assertAlmostEqual(float(d[0, 1]), 0.0, places=14)


class JacobianTests(unittest.TestCase):
    def _rectangle_xy(self, width: float, height: float) -> np.ndarray:
        return np.array(
            [
                [0.0, 0.0],
                [width, 0.0],
                [width, height],
                [0.0, height],
                [width / 2.0, 0.0],
                [width, height / 2.0],
                [width / 2.0, height],
                [0.0, height / 2.0],
            ],
            dtype=float,
        )

    def test_rectangle_determinant_at_center(self) -> None:
        w, h = 2.0, 3.0
        xy = self._rectangle_xy(w, h)
        _, det_j, _ = q8_jacobian(0.0, 0.0, xy)
        self.assertAlmostEqual(det_j, w * h / 4.0, places=10)

    def test_non_positive_jacobian_raises(self) -> None:
        xy_degenerate = np.zeros((8, 2), dtype=float)
        with self.assertRaises(ValueError):
            q8_jacobian(0.0, 0.0, xy_degenerate)

    def test_physical_derivatives_sum_zero_for_partition_of_unity(self) -> None:
        xy = self._rectangle_xy(2.0, 1.0)
        for xi, eta in ((0.0, 0.0), (0.25, -0.4), (-0.6, 0.7)):
            _, d_w, _ = physical_derivatives_q8(xi, eta, xy)
            self.assertAlmostEqual(float(np.sum(d_w[0])), 0.0, places=10)
            self.assertAlmostEqual(float(np.sum(d_w[1])), 0.0, places=10)
            _, d_rot, _ = physical_derivatives_q9(xi, eta, xy)
            self.assertAlmostEqual(float(np.sum(d_rot[0])), 0.0, places=10)
            self.assertAlmostEqual(float(np.sum(d_rot[1])), 0.0, places=10)


class HeterosisStiffnessCoreTests(unittest.TestCase):
    def _rectangle_xy(self, width: float, height: float) -> np.ndarray:
        return np.array(
            [
                [0.0, 0.0],
                [width, 0.0],
                [width, height],
                [0.0, height],
                [width / 2.0, 0.0],
                [width, height / 2.0],
                [width / 2.0, height],
                [0.0, height / 2.0],
            ],
            dtype=float,
        )

    def test_stiffness_symmetric_and_size(self) -> None:
        xy = self._rectangle_xy(2.0, 1.0)
        k = heterosis_element_stiffness(xy, young_modulus=200_000.0, poisson_ratio=0.25, thickness=20.0)
        self.assertEqual(k.shape, (NUM_DOF, NUM_DOF))
        self.assertTrue(np.allclose(k, k.T, atol=1e-9))

    def test_stiffness_has_nonzero_bending_and_shear_contributions(self) -> None:
        xy = self._rectangle_xy(2.0, 1.0)
        k = heterosis_element_stiffness(xy, young_modulus=200_000.0, poisson_ratio=0.25, thickness=20.0)
        self.assertGreater(np.trace(k), 0.0)
        # w and rotation blocks should pick up stiffness
        self.assertGreater(np.linalg.norm(k[0:8, 0:8]), 0.0)
        self.assertGreater(np.linalg.norm(k[8:17, 8:17]), 0.0)

    def test_bending_contribution_spd_at_sample_point(self) -> None:
        """K_b = B_b^T D_b B_b * detJ is symmetric PSD at a sample (xi, eta)."""
        xy = self._rectangle_xy(2.0, 1.0)
        xi, eta = 0.2, -0.15
        bb, det_j = bending_B_matrix(xi, eta, xy)
        d_b = mindlin_bending_matrix(200_000.0, 0.25, 20.0)
        ke_b = bb.T @ d_b @ bb * det_j
        self.assertEqual(ke_b.shape, (NUM_DOF, NUM_DOF))
        self.assertTrue(np.allclose(ke_b, ke_b.T))
        self.assertGreater(np.trace(ke_b), 0.0)
        eig = np.linalg.eigvalsh(0.5 * (ke_b + ke_b.T))
        self.assertGreaterEqual(float(eig.min()), -1e-6)

    def test_shear_contribution_spd_at_sample_point(self) -> None:
        xy = self._rectangle_xy(2.0, 1.0)
        xi, eta = -0.1, 0.25
        bs, det_j = shear_B_matrix(xi, eta, xy)
        d_s = mindlin_shear_matrix(200_000.0, 0.25, 20.0)
        ke_s = bs.T @ d_s @ bs * det_j
        self.assertTrue(np.allclose(ke_s, ke_s.T))
        eig = np.linalg.eigvalsh(0.5 * (ke_s + ke_s.T))
        self.assertGreaterEqual(float(eig.min()), -1e-6)


class DofsTests(unittest.TestCase):
    def test_num_dof(self) -> None:
        self.assertEqual(NUM_DOF, 26)


if __name__ == "__main__":
    unittest.main()
