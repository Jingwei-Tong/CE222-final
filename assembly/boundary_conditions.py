from __future__ import annotations

import numpy as np
from scipy import sparse

from assembly.dof_map import DofMap
from config import ProblemConfig
from mesh import StructuredPatchMesh


def clamped_dofs(mesh: StructuredPatchMesh, dof_map: DofMap, config: ProblemConfig) -> np.ndarray:
    node_ids: set[int] = set()
    for edge_name in config.clamped_edges:
        node_ids.update(mesh.boundary_nodes[edge_name])

    constrained = []
    for node_id in sorted(node_ids):
        constrained.extend(dof_map.node_dofs(node_id))

    return np.array(constrained, dtype=int)


def apply_clamped_bc(
    k_full: sparse.spmatrix | np.ndarray, f_full: np.ndarray, constrained_dofs: np.ndarray
) -> tuple[sparse.spmatrix | np.ndarray, np.ndarray, np.ndarray]:
    constrained_unique = np.unique(constrained_dofs.astype(int))
    all_dofs = np.arange(k_full.shape[0], dtype=int)
    free_dofs = np.setdiff1d(all_dofs, constrained_unique, assume_unique=True)
    if sparse.issparse(k_full):
        k_reduced = k_full.tocsr()[free_dofs][:, free_dofs]
    else:
        k_reduced = k_full[np.ix_(free_dofs, free_dofs)]
    f_reduced = f_full[free_dofs]
    return k_reduced, f_reduced, free_dofs


def expand_solution(u_free: np.ndarray, free_dofs: np.ndarray, total_dof: int) -> np.ndarray:
    u_full = np.zeros(total_dof, dtype=float)
    u_full[free_dofs] = u_free
    return u_full
