from __future__ import annotations

from dataclasses import dataclass

from config import ProblemConfig, VALID_EDGES


EDGE_LOCAL_Q8_NODES = {
    0: (0, 1, 4),  # bottom
    1: (1, 2, 5),  # right
    2: (2, 3, 6),  # top
    3: (3, 0, 7),  # left
}

EDGE_NAMES = {
    0: "bottom",
    1: "right",
    2: "top",
    3: "left",
}


@dataclass(frozen=True)
class MeshSpec:
    nx_side: int = 1
    nx_hole: int = 1
    ny_side: int = 1
    ny_hole: int = 1

    def __post_init__(self) -> None:
        if min(self.nx_side, self.nx_hole, self.ny_side, self.ny_hole) < 1:
            raise ValueError("All mesh subdivision counts must be at least 1.")
        if self.nx_side != self.ny_side:
            raise ValueError(
                "nx_side must equal ny_side so patches meeting on each outer "
                '"corner connector" edge use the same edge subdivision; otherwise '
                "those interfaces get non-coincident nodes. "
                f"Got nx_side={self.nx_side}, ny_side={self.ny_side}."
            )


@dataclass(frozen=True)
class QuadElement:
    element_id: int
    patch_name: str
    q8_nodes: tuple[int, ...]
    q9_nodes: tuple[int, ...]


@dataclass(frozen=True)
class BoundaryEdge:
    edge_name: str
    element_id: int
    local_edge_index: int
    q8_nodes: tuple[int, ...]


@dataclass(frozen=True)
class StructuredPatchMesh:
    nodes: tuple[tuple[float, float], ...]
    elements: tuple[QuadElement, ...]
    boundary_nodes: dict[str, tuple[int, ...]]
    boundary_edges: dict[str, tuple[BoundaryEdge, ...]]
    spec: MeshSpec


def generate_mesh(config: ProblemConfig, spec: MeshSpec | None = None) -> StructuredPatchMesh:
    spec = spec or MeshSpec()
    node_lookup: dict[tuple[float, float], int] = {}
    nodes: list[tuple[float, float]] = []
    elements: list[QuadElement] = []

    patch_quads = _build_patch_quads(config)
    patch_divisions = {
        "top": (spec.nx_hole, spec.ny_side),
        "right": (spec.nx_side, spec.ny_hole),
        "bottom": (spec.nx_hole, spec.ny_side),
        "left": (spec.nx_side, spec.ny_hole),
    }

    def get_or_create_node(x: float, y: float) -> int:
        key = (round(x, 12), round(y, 12))
        if key not in node_lookup:
            node_lookup[key] = len(nodes)
            nodes.append((float(x), float(y)))
        return node_lookup[key]

    for patch_name, corners in patch_quads.items():
        nx_patch, ny_patch = patch_divisions[patch_name]
        s_values = [i / (2 * nx_patch) for i in range(2 * nx_patch + 1)]
        t_values = [j / (2 * ny_patch) for j in range(2 * ny_patch + 1)]

        patch_node_ids = [[-1 for _ in t_values] for _ in s_values]
        for i, s in enumerate(s_values):
            for j, t in enumerate(t_values):
                x, y = _bilinear_map(corners, s, t)
                patch_node_ids[i][j] = get_or_create_node(x, y)

        for ex in range(nx_patch):
            for ey in range(ny_patch):
                i = 2 * ex
                j = 2 * ey
                q9_nodes = (
                    patch_node_ids[i][j],
                    patch_node_ids[i + 2][j],
                    patch_node_ids[i + 2][j + 2],
                    patch_node_ids[i][j + 2],
                    patch_node_ids[i + 1][j],
                    patch_node_ids[i + 2][j + 1],
                    patch_node_ids[i + 1][j + 2],
                    patch_node_ids[i][j + 1],
                    patch_node_ids[i + 1][j + 1],
                )
                q8_nodes = q9_nodes[:8]
                elements.append(
                    QuadElement(
                        element_id=len(elements),
                        patch_name=patch_name,
                        q8_nodes=q8_nodes,
                        q9_nodes=q9_nodes,
                    )
                )

    boundary_nodes = identify_boundary_nodes(tuple(nodes), config)
    boundary_edges = identify_boundary_edges(tuple(nodes), tuple(elements), config)

    return StructuredPatchMesh(
        nodes=tuple(nodes),
        elements=tuple(elements),
        boundary_nodes=boundary_nodes,
        boundary_edges=boundary_edges,
        spec=spec,
    )


def identify_boundary_nodes(
    nodes: tuple[tuple[float, float], ...], config: ProblemConfig, tol: float = 1e-9
) -> dict[str, tuple[int, ...]]:
    boundary_nodes: dict[str, tuple[int, ...]] = {}
    for edge_name in VALID_EDGES:
        ids = [
            node_id
            for node_id, (x, y) in enumerate(nodes)
            if _point_on_boundary(x, y, edge_name, config, tol=tol)
        ]
        boundary_nodes[edge_name] = tuple(ids)
    return boundary_nodes


def identify_boundary_edges(
    nodes: tuple[tuple[float, float], ...],
    elements: tuple[QuadElement, ...],
    config: ProblemConfig,
    tol: float = 1e-9,
) -> dict[str, tuple[BoundaryEdge, ...]]:
    boundary_edges: dict[str, list[BoundaryEdge]] = {edge_name: [] for edge_name in VALID_EDGES}

    for element in elements:
        for local_edge_index, local_q8_ids in EDGE_LOCAL_Q8_NODES.items():
            q8_nodes = tuple(element.q8_nodes[i] for i in local_q8_ids)
            coords = [nodes[node_id] for node_id in q8_nodes]
            for edge_name in VALID_EDGES:
                if all(_point_on_boundary(x, y, edge_name, config, tol=tol) for x, y in coords):
                    boundary_edges[edge_name].append(
                        BoundaryEdge(
                            edge_name=edge_name,
                            element_id=element.element_id,
                            local_edge_index=local_edge_index,
                            q8_nodes=q8_nodes,
                        )
                    )

    return {name: tuple(edges) for name, edges in boundary_edges.items()}


def _build_patch_quads(
    config: ProblemConfig,
) -> dict[str, tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]]:
    o1 = (0.0, 0.0)
    o2 = (config.outer_width, 0.0)
    o3 = (config.outer_width, config.outer_height)
    o4 = (0.0, config.outer_height)

    i1 = (config.hole_x_min, config.hole_y_min)
    i2 = (config.hole_x_max, config.hole_y_min)
    i3 = (config.hole_x_max, config.hole_y_max)
    i4 = (config.hole_x_min, config.hole_y_max)

    return {
        "top": (i4, i3, o3, o4),
        "right": (i2, o2, o3, i3),
        "bottom": (o1, o2, i2, i1),
        "left": (o1, i1, i4, o4),
    }


def _bilinear_map(
    corners: tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]],
    s: float,
    t: float,
) -> tuple[float, float]:
    p00, p10, p11, p01 = corners
    n00 = (1.0 - s) * (1.0 - t)
    n10 = s * (1.0 - t)
    n11 = s * t
    n01 = (1.0 - s) * t
    x = n00 * p00[0] + n10 * p10[0] + n11 * p11[0] + n01 * p01[0]
    y = n00 * p00[1] + n10 * p10[1] + n11 * p11[1] + n01 * p01[1]
    return x, y


def _point_on_boundary(
    x: float, y: float, edge_name: str, config: ProblemConfig, tol: float = 1e-9
) -> bool:
    if edge_name == "left":
        return abs(x) <= tol
    if edge_name == "right":
        return abs(x - config.outer_width) <= tol
    if edge_name == "bottom":
        return abs(y) <= tol
    if edge_name == "top":
        return abs(y - config.outer_height) <= tol
    if edge_name == "hole_left":
        return abs(x - config.hole_x_min) <= tol and config.hole_y_min - tol <= y <= config.hole_y_max + tol
    if edge_name == "hole_right":
        return abs(x - config.hole_x_max) <= tol and config.hole_y_min - tol <= y <= config.hole_y_max + tol
    if edge_name == "hole_bottom":
        return abs(y - config.hole_y_min) <= tol and config.hole_x_min - tol <= x <= config.hole_x_max + tol
    if edge_name == "hole_top":
        return abs(y - config.hole_y_max) <= tol and config.hole_x_min - tol <= x <= config.hole_x_max + tol
    raise ValueError(f"Unsupported edge name: {edge_name}")
