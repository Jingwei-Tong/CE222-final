from __future__ import annotations

import numpy as np


def q8_natural_nodes() -> np.ndarray:
    """Q8 node coords in (xi, eta), order: BL, BR, TR, TL, Bm, Rm, Tm, Lm."""
    return np.array(
        [
            [-1.0, -1.0],
            [1.0, -1.0],
            [1.0, 1.0],
            [-1.0, 1.0],
            [0.0, -1.0],
            [1.0, 0.0],
            [0.0, 1.0],
            [-1.0, 0.0],
        ],
        dtype=float,
    )


def q9_natural_nodes() -> np.ndarray:
    """Q9 node coords, order: BL, BR, TR, TL, Bm, Rm, Tm, Lm, C."""
    corners_edges = q8_natural_nodes()
    center = np.array([[0.0, 0.0]], dtype=float)
    return np.vstack((corners_edges, center))


def q8_shape(xi: float, eta: float) -> tuple[np.ndarray, np.ndarray]:
    """Serendipity Q8 shape functions and dN/d(xi,eta) stacked as (2, 8)."""
    n = np.array(
        [
            0.25 * (1.0 - xi) * (1.0 - eta) * (-xi - eta - 1.0),
            0.25 * (1.0 + xi) * (1.0 - eta) * (xi - eta - 1.0),
            0.25 * (1.0 + xi) * (1.0 + eta) * (xi + eta - 1.0),
            0.25 * (1.0 - xi) * (1.0 + eta) * (-xi + eta - 1.0),
            0.5 * (1.0 - xi**2) * (1.0 - eta),
            0.5 * (1.0 + xi) * (1.0 - eta**2),
            0.5 * (1.0 - xi**2) * (1.0 + eta),
            0.5 * (1.0 - xi) * (1.0 - eta**2),
        ]
    )
    d_dxi = np.array(
        [
            0.25 * (1.0 - eta) * (2.0 * xi + eta),
            0.25 * (1.0 - eta) * (2.0 * xi - eta),
            0.25 * (1.0 + eta) * (2.0 * xi + eta),
            0.25 * (1.0 + eta) * (2.0 * xi - eta),
            -xi * (1.0 - eta),
            0.5 * (1.0 - eta**2),
            -xi * (1.0 + eta),
            -0.5 * (1.0 - eta**2),
        ]
    )
    d_deta = np.array(
        [
            0.25 * (1.0 - xi) * (xi + 2.0 * eta),
            0.25 * (1.0 + xi) * (-xi + 2.0 * eta),
            0.25 * (1.0 + xi) * (xi + 2.0 * eta),
            0.25 * (1.0 - xi) * (-xi + 2.0 * eta),
            -0.5 * (1.0 - xi**2),
            -(1.0 + xi) * eta,
            0.5 * (1.0 - xi**2),
            -(1.0 - xi) * eta,
        ]
    )
    return n, np.vstack((d_dxi, d_deta))


def q9_shape(xi: float, eta: float) -> tuple[np.ndarray, np.ndarray]:
    """Lagrange Q9 shape functions and derivatives (2, 9)."""
    l1_x, l2_x, l3_x = 0.5 * xi * (xi - 1.0), 1.0 - xi**2, 0.5 * xi * (xi + 1.0)
    l1_y, l2_y, l3_y = 0.5 * eta * (eta - 1.0), 1.0 - eta**2, 0.5 * eta * (eta + 1.0)
    dl1_x, dl2_x, dl3_x = xi - 0.5, -2.0 * xi, xi + 0.5
    dl1_y, dl2_y, dl3_y = eta - 0.5, -2.0 * eta, eta + 0.5

    n = np.array(
        [
            l1_x * l1_y,
            l3_x * l1_y,
            l3_x * l3_y,
            l1_x * l3_y,
            l2_x * l1_y,
            l3_x * l2_y,
            l2_x * l3_y,
            l1_x * l2_y,
            l2_x * l2_y,
        ]
    )
    d_dxi = np.array(
        [
            dl1_x * l1_y,
            dl3_x * l1_y,
            dl3_x * l3_y,
            dl1_x * l3_y,
            dl2_x * l1_y,
            dl3_x * l2_y,
            dl2_x * l3_y,
            dl1_x * l2_y,
            dl2_x * l2_y,
        ]
    )
    d_deta = np.array(
        [
            l1_x * dl1_y,
            l3_x * dl1_y,
            l3_x * dl3_y,
            l1_x * dl3_y,
            l2_x * dl1_y,
            l3_x * dl2_y,
            l2_x * dl3_y,
            l1_x * dl2_y,
            l2_x * dl2_y,
        ]
    )
    return n, np.vstack((d_dxi, d_deta))
