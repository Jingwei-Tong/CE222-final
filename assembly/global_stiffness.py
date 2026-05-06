from __future__ import annotations

import numpy as np
from scipy import sparse

from assembly.dof_map import DofMap
from config import ProblemConfig
from element import heterosis_element_stiffness
from mesh import QuadElement, StructuredPatchMesh


def element_q8_coordinates(mesh: StructuredPatchMesh, element: QuadElement) -> np.ndarray:
    return np.array([mesh.nodes[node_id] for node_id in element.q8_nodes], dtype=float)


def assemble_global_stiffness(
    mesh: StructuredPatchMesh, dof_map: DofMap, config: ProblemConfig
) -> sparse.csr_matrix:
    rows: list[np.ndarray] = []
    cols: list[np.ndarray] = []
    data: list[np.ndarray] = []

    for element in mesh.elements:
        xy_q8 = element_q8_coordinates(mesh, element)
        k_local = heterosis_element_stiffness(
            xy_q8,
            young_modulus=config.young_modulus,
            poisson_ratio=config.poisson_ratio,
            thickness=config.thickness,
        )
        element_dofs = dof_map.element_dofs(element)
        rows.append(np.repeat(element_dofs, len(element_dofs)))
        cols.append(np.tile(element_dofs, len(element_dofs)))
        data.append(k_local.ravel())

    if not data:
        return sparse.csr_matrix((dof_map.num_dof, dof_map.num_dof), dtype=float)

    k_global = sparse.coo_matrix(
        (np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))),
        shape=(dof_map.num_dof, dof_map.num_dof),
        dtype=float,
    ).tocsr()
    return 0.5 * (k_global + k_global.T)
