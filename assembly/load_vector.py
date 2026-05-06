from __future__ import annotations

import numpy as np

from assembly.dof_map import DofMap
from assembly.global_stiffness import element_q8_coordinates
from config import ProblemConfig
from element import heterosis_element_edge_load_vector
from mesh import StructuredPatchMesh


EDGE_LOAD_SIGNS = {
    "top": 1.0,
    "bottom": -1.0,
    "hole_top": -1.0,
}


def assemble_global_load(mesh: StructuredPatchMesh, dof_map: DofMap, config: ProblemConfig) -> np.ndarray:
    f_global = np.zeros(dof_map.num_dof, dtype=float)

    loaded_edges = config.loaded_edges
    if loaded_edges is None:
        loaded_edges = tuple(edge_name for edge_name in EDGE_LOAD_SIGNS if edge_name in config.free_edges)

    for edge_name in loaded_edges:
        if edge_name not in EDGE_LOAD_SIGNS:
            raise ValueError(f"Unsupported loaded edge: {edge_name}")
        sign = EDGE_LOAD_SIGNS[edge_name]
        if edge_name not in mesh.boundary_edges:
            continue
        for boundary_edge in mesh.boundary_edges[edge_name]:
            element = mesh.elements[boundary_edge.element_id]
            xy_q8 = element_q8_coordinates(mesh, element)
            f_local = heterosis_element_edge_load_vector(
                xy_q8,
                local_edge_index=boundary_edge.local_edge_index,
                line_load_w=sign * config.applied_shear,
            )
            element_dofs = dof_map.element_dofs(element)
            f_global[element_dofs] += f_local

    return f_global
