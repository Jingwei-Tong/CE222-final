from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mesh import QuadElement, StructuredPatchMesh


@dataclass(frozen=True)
class DofMap:
    num_nodes: int
    w_nodes: tuple[int, ...]

    @property
    def num_w_dof(self) -> int:
        return len(self.w_nodes)

    @property
    def num_dof(self) -> int:
        return self.num_w_dof + 2 * self.num_nodes

    @property
    def tx_offset(self) -> int:
        return self.num_w_dof

    @property
    def ty_offset(self) -> int:
        return self.num_w_dof + self.num_nodes

    def has_w_dof(self, node_id: int) -> bool:
        return node_id in self.w_nodes

    def _w_position(self, node_id: int) -> int:
        try:
            return self.w_nodes.index(node_id)
        except ValueError as exc:
            raise ValueError(f"Node {node_id} does not carry a Q8 transverse-displacement DOF.") from exc

    def w_dof(self, node_id: int) -> int:
        return self._w_position(node_id)

    def tx_dof(self, node_id: int) -> int:
        return self.tx_offset + node_id

    def ty_dof(self, node_id: int) -> int:
        return self.ty_offset + node_id

    def node_dofs(self, node_id: int) -> tuple[int, int, int]:
        return (self.w_dof(node_id), self.tx_dof(node_id), self.ty_dof(node_id))

    def element_dofs(self, element: QuadElement) -> np.ndarray:
        q8_w = [self.w_dof(node_id) for node_id in element.q8_nodes]
        q9_tx = [self.tx_dof(node_id) for node_id in element.q9_nodes]
        q9_ty = [self.ty_dof(node_id) for node_id in element.q9_nodes]
        return np.array(q8_w + q9_tx + q9_ty, dtype=int)


def build_dof_map(mesh: StructuredPatchMesh) -> DofMap:
    w_nodes = tuple(sorted({node_id for element in mesh.elements for node_id in element.q8_nodes}))
    return DofMap(num_nodes=len(mesh.nodes), w_nodes=w_nodes)
