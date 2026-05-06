from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
from scipy import sparse
from scipy.sparse import linalg as sparse_linalg


@dataclass(frozen=True)
class LinearSolveResult:
    u_free: np.ndarray
    residual: np.ndarray
    residual_norm: float
    num_free_dof: int


def solve_system(k_reduced: sparse.spmatrix | np.ndarray, f_reduced: np.ndarray) -> LinearSolveResult:
    if len(k_reduced.shape) != 2 or k_reduced.shape[0] != k_reduced.shape[1]:
        raise ValueError("k_reduced must be a square 2D matrix.")
    if f_reduced.ndim != 1:
        raise ValueError("f_reduced must be a 1D vector.")
    if k_reduced.shape[0] != f_reduced.shape[0]:
        raise ValueError("k_reduced and f_reduced must have compatible dimensions.")
    if k_reduced.shape[0] == 0:
        raise ValueError("Reduced system has zero free DOFs.")

    try:
        if sparse.issparse(k_reduced):
            with warnings.catch_warnings():
                warnings.simplefilter("error", sparse_linalg.MatrixRankWarning)
                u_free = sparse_linalg.spsolve(k_reduced.tocsr(), f_reduced)
        else:
            u_free = np.linalg.solve(k_reduced, f_reduced)
    except (np.linalg.LinAlgError, sparse_linalg.MatrixRankWarning) as exc:
        raise np.linalg.LinAlgError(f"Failed to solve reduced system: {exc}") from exc

    u_free = np.asarray(u_free, dtype=float)
    if not np.all(np.isfinite(u_free)):
        raise np.linalg.LinAlgError("Failed to solve reduced system: non-finite solution encountered.")

    residual = np.asarray(k_reduced @ u_free - f_reduced, dtype=float)
    return LinearSolveResult(
        u_free=u_free,
        residual=residual,
        residual_norm=float(np.linalg.norm(residual)),
        num_free_dof=int(f_reduced.shape[0]),
    )
