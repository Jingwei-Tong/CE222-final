from __future__ import annotations

import numpy as np


def mindlin_bending_matrix(
    young_modulus: float, poisson_ratio: float, thickness: float
) -> np.ndarray:
    """Plane-stress bending D for Mindlin plate (3x3): [kappa_x, kappa_y, gamma_xy]."""
    e, nu = young_modulus, poisson_ratio
    t = thickness
    factor = e * t**3 / (12.0 * (1.0 - nu**2))
    return factor * np.array(
        [
            [1.0, nu, 0.0],
            [nu, 1.0, 0.0],
            [0.0, 0.0, 0.5 * (1.0 - nu)],
        ],
        dtype=float,
    )


def mindlin_shear_matrix(
    young_modulus: float,
    poisson_ratio: float,
    thickness: float,
    shear_correction: float = 5.0 / 6.0,
) -> np.ndarray:
    """Transverse shear Ds (2x2) for [gamma_xz, gamma_yz]."""
    g = young_modulus / (2.0 * (1.0 + poisson_ratio))
    kappa = shear_correction * g * thickness
    return kappa * np.eye(2, dtype=float)
