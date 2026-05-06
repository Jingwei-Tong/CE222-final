from __future__ import annotations

import numpy as np

from .shapes import q8_shape


def q8_jacobian(xi: float, eta: float, xy_q8: np.ndarray) -> tuple[np.ndarray, float, np.ndarray]:
    """xy_q8: (8, 2) physical coords for Q8 nodes. Returns J, detJ, invJ."""
    _, d_parent = q8_shape(xi, eta)
    jacobian = d_parent @ xy_q8
    det_j = float(np.linalg.det(jacobian))
    if det_j <= 0.0:
        raise ValueError(f"Non-positive Jacobian determinant: {det_j}")
    return jacobian, det_j, np.linalg.inv(jacobian)


def physical_derivatives_q8(
    xi: float, eta: float, xy_q8: np.ndarray
) -> tuple[np.ndarray, np.ndarray, float]:
    n, d_parent = q8_shape(xi, eta)
    _, det_j, inv_j = q8_jacobian(xi, eta, xy_q8)
    d_phys = inv_j @ d_parent
    return n, d_phys, det_j


def physical_derivatives_q9(
    xi: float, eta: float, xy_q8: np.ndarray
) -> tuple[np.ndarray, np.ndarray, float]:
    from .shapes import q9_shape

    n, d_parent = q9_shape(xi, eta)
    _, det_j, inv_j = q8_jacobian(xi, eta, xy_q8)
    d_phys = inv_j @ d_parent
    return n, d_phys, det_j
