"""
Heterosis Mindlin plate element: transverse deflection w on Q8, rotations (theta_x, theta_y) on Q9.

DOF order (26 total), aligned with mesh q8 / q9 node numbering:
  0–7   : w at Q8 nodes (BL, BR, TR, TL, Bm, Rm, Tm, Lm in parent (xi, eta)).
  8–16  : theta_x at Q9 nodes (eight serendipity + center).
  17–25 : theta_y at Q9 nodes.

Integration: bending stiffness uses 3x3 Gauss; transverse shear stiffness uses 2x2 (selective reduced).

Sign: transverse shear strains gamma_xz = dw/dx - theta_x, gamma_yz = dw/dy - theta_y.
"""

from __future__ import annotations

import numpy as np

from .b_matrix import bending_B_matrix, shear_B_matrix
from .constitutive import mindlin_bending_matrix, mindlin_shear_matrix
from .dofs import SLICE_W
from .quadrature import gauss_1d, gauss_2x2, gauss_3x3
from .shapes import q8_shape


def heterosis_element_stiffness(
    xy_q8: np.ndarray,
    young_modulus: float,
    poisson_ratio: float,
    thickness: float,
    shear_correction: float = 5.0 / 6.0,
) -> np.ndarray:
    """
    Heterosis plate element: w interpolated with Q8, theta_x/y with Q9.
    Bending: 3x3 Gauss. Shear: 2x2 Gauss.
    xy_q8: (8, 2) corner+edge-mid physical coordinates (same as mesh q8_nodes order).
    """
    d_b = mindlin_bending_matrix(young_modulus, poisson_ratio, thickness)
    d_s = mindlin_shear_matrix(young_modulus, poisson_ratio, thickness, shear_correction)

    k = np.zeros((26, 26), dtype=float)

    for gp in gauss_3x3():
        bb, det_j = bending_B_matrix(gp.xi, gp.eta, xy_q8)
        k += bb.T @ d_b @ bb * det_j * gp.weight

    for gp in gauss_2x2():
        bs, det_j = shear_B_matrix(gp.xi, gp.eta, xy_q8)
        k += bs.T @ d_s @ bs * det_j * gp.weight

    return 0.5 * (k + k.T)


def heterosis_element_edge_load_vector(
    xy_q8: np.ndarray,
    local_edge_index: int,
    line_load_w: float,
) -> np.ndarray:
    """
    Equivalent nodal load (26,) from a constant prescribed transverse line load on one element edge.

    Only the w (Q8) block is filled; rotations have zero load from this traction model.

    Parameters
    ----------
    xy_q8 :
        (8, 2) physical coordinates for the Q8 nodes.
    local_edge_index :
        Parent-edge index consistent with mesh.EDGE_NAMES / EDGE_LOCAL_Q8_NODES:
        0 bottom (eta=-1), 1 right (xi=+1), 2 top (eta=+1), 3 left (xi=-1).
    line_load_w :
        Constant line load (force per unit arc length) in the +w direction on that edge.
    """
    if local_edge_index not in (0, 1, 2, 3):
        raise ValueError(f"local_edge_index must be 0..3, got {local_edge_index}")

    fe = np.zeros(26, dtype=float)
    for u, w in gauss_1d(3):
        xi, eta = _parent_coords_on_edge(local_edge_index, u)
        n, _ = q8_shape(xi, eta)
        scale = _edge_jacobian_scale(xi, eta, xy_q8, local_edge_index)
        fe[SLICE_W] += line_load_w * n * w * scale
    return fe


def _parent_coords_on_edge(local_edge_index: int, u: float) -> tuple[float, float]:
    if local_edge_index == 0:
        return u, -1.0
    if local_edge_index == 1:
        return 1.0, u
    if local_edge_index == 2:
        return u, 1.0
    return -1.0, u


def _edge_jacobian_scale(xi: float, eta: float, xy_q8: np.ndarray, local_edge_index: int) -> float:
    """Physical arc-length factor |d x / d u| on the parent edge parameter u in [-1, 1]."""
    if local_edge_index == 0:
        u = xi
        edge_node_ids = (0, 1, 4)
    elif local_edge_index == 1:
        u = eta
        edge_node_ids = (1, 2, 5)
    elif local_edge_index == 2:
        u = xi
        edge_node_ids = (3, 2, 6)
    else:
        u = eta
        edge_node_ids = (0, 3, 7)

    d_edge = np.array([u - 0.5, u + 0.5, -2.0 * u], dtype=float)
    tang = d_edge @ xy_q8[list(edge_node_ids)]
    return float(np.linalg.norm(tang))


def bending_strain_operator_at(
    xi: float, eta: float, xy_q8: np.ndarray
) -> tuple[np.ndarray, float]:
    """Returns B_b (3, 26) and detJ at (xi, eta) for debugging/tests."""
    return bending_B_matrix(xi, eta, xy_q8)


def shear_strain_operator_at(
    xi: float, eta: float, xy_q8: np.ndarray
) -> tuple[np.ndarray, float]:
    """Returns B_s (2, 26) and detJ."""
    return shear_B_matrix(xi, eta, xy_q8)
