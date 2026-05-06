from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from assembly.dof_map import build_dof_map
from config import ProblemConfig
from mesh import MeshSpec, generate_mesh


class DofMapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mesh = generate_mesh(ProblemConfig(), MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1))
        self.dof_map = build_dof_map(self.mesh)

    def test_num_dof_matches_q8_plus_two_q9_blocks(self) -> None:
        q8_nodes = {node_id for element in self.mesh.elements for node_id in element.q8_nodes}
        self.assertEqual(self.dof_map.num_w_dof, len(q8_nodes))
        self.assertEqual(self.dof_map.num_dof, len(q8_nodes) + 2 * len(self.mesh.nodes))

    def test_each_q8_node_has_unique_triplet(self) -> None:
        dofs = []
        for node_id in self.dof_map.w_nodes:
            dofs.extend(self.dof_map.node_dofs(node_id))
        self.assertEqual(len(dofs), len(set(dofs)))

    def test_center_q9_node_has_no_w_dof(self) -> None:
        center_only_nodes = sorted(
            {node_id for element in self.mesh.elements for node_id in element.q9_nodes}
            - {node_id for element in self.mesh.elements for node_id in element.q8_nodes}
        )
        self.assertGreater(len(center_only_nodes), 0)
        with self.assertRaises(ValueError):
            self.dof_map.w_dof(center_only_nodes[0])

    def test_element_dofs_follow_local_order(self) -> None:
        element = self.mesh.elements[0]
        element_dofs = self.dof_map.element_dofs(element)
        self.assertEqual(len(element_dofs), 26)
        self.assertEqual(list(element_dofs[:8]), [self.dof_map.w_dof(node_id) for node_id in element.q8_nodes])
        self.assertEqual(
            list(element_dofs[8:17]),
            [self.dof_map.tx_dof(node_id) for node_id in element.q9_nodes],
        )
        self.assertEqual(
            list(element_dofs[17:26]),
            [self.dof_map.ty_dof(node_id) for node_id in element.q9_nodes],
        )


if __name__ == "__main__":
    unittest.main()
