from __future__ import annotations

from assembly import build_dof_map
from config import ProblemConfig
from mesh import StructuredPatchMesh


def find_node_at_point(
    mesh: StructuredPatchMesh, point: tuple[float, float], tol: float = 1e-9
) -> int | None:
    x_q, y_q = point
    for node_id, (x, y) in enumerate(mesh.nodes):
        if abs(x - x_q) <= tol and abs(y - y_q) <= tol:
            return node_id
    return None


def query_point_deflection(
    solution: object,
    mesh: StructuredPatchMesh,
    point: tuple[float, float],
    tol: float = 1e-9,
) -> float:
    """
    Return transverse deflection w at a query point when that point coincides with a Q8 node.

    For the current project stage, point queries are nodal-only. Interpolation inside an element
    can be added later once a full post-processing layer is in place.
    """
    node_id = find_node_at_point(mesh, point, tol=tol)
    if node_id is None:
        raise ValueError(f"Query point {point} does not coincide with a mesh node.")

    dof_map = build_dof_map(mesh)
    if not dof_map.has_w_dof(node_id):
        raise ValueError(f"Mesh node {node_id} at {point} does not carry a Q8 w DOF.")

    return float(solution[dof_map.w_dof(node_id)])


def query_point_A_deflection(solution: object, mesh: StructuredPatchMesh, config: ProblemConfig) -> float:
    return query_point_deflection(solution, mesh, config.point_A_coordinates)
