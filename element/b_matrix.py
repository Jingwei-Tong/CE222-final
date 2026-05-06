"""Mindlin plate strain–displacement operators for the heterosis Q8–w / Q9–θ element."""

from __future__ import annotations

import numpy as np

from .dofs import NUM_DOF, SLICE_TX, SLICE_TY, SLICE_W
from .jacobian import physical_derivatives_q8, physical_derivatives_q9


def bending_B_matrix(xi: float, eta: float, xy_q8: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Bending B_b (3, 26): [kappa_x, kappa_y, gamma_xy]^T from rotations theta_x, theta_y (Q9).
    Curvatures kappa_x = d(theta_x)/dx, kappa_y = d(theta_y)/dy, gamma_xy = d(theta_x)/dy + d(theta_y)/dx.
    """
    _, d_rot, det_j = physical_derivatives_q9(xi, eta, xy_q8)
    bb = np.zeros((3, NUM_DOF), dtype=float)
    for i in range(9):
        bb[0, SLICE_TX.start + i] = d_rot[0, i]
        bb[1, SLICE_TY.start + i] = d_rot[1, i]
        bb[2, SLICE_TX.start + i] = d_rot[1, i]
        bb[2, SLICE_TY.start + i] = d_rot[0, i]
    return bb, det_j


def shear_B_matrix(xi: float, eta: float, xy_q8: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Transverse shear B_s (2, 26): [gamma_xz, gamma_yz]^T with
    gamma_xz = dw/dx - theta_x, gamma_yz = dw/dy - theta_y (Mindlin).
    """
    _, d_w, det_j = physical_derivatives_q8(xi, eta, xy_q8)
    n_rot, _, _ = physical_derivatives_q9(xi, eta, xy_q8)
    bs = np.zeros((2, NUM_DOF), dtype=float)
    for i in range(8):
        bs[0, SLICE_W.start + i] = d_w[0, i]
        bs[1, SLICE_W.start + i] = d_w[1, i]
    for i in range(9):
        bs[0, SLICE_TX.start + i] = -n_rot[i]
        bs[1, SLICE_TY.start + i] = -n_rot[i]
    return bs, det_j
