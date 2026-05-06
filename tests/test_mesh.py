from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import ProblemConfig
from mesh import MeshSpec, generate_mesh


class MeshModuleTests(unittest.TestCase):
    def test_coarse_mesh_has_expected_counts(self) -> None:
        mesh = generate_mesh(ProblemConfig(), MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1))
        self.assertEqual(len(mesh.elements), 4)
        self.assertEqual(len(mesh.nodes), 24)

    def test_elements_have_q8_and_q9_connectivity(self) -> None:
        mesh = generate_mesh(ProblemConfig(), MeshSpec())
        for element in mesh.elements:
            self.assertEqual(len(element.q8_nodes), 8)
            self.assertEqual(len(element.q9_nodes), 9)

    def test_no_nodes_are_created_inside_the_hole(self) -> None:
        config = ProblemConfig()
        mesh = generate_mesh(config, MeshSpec(nx_side=2, nx_hole=2, ny_side=2, ny_hole=2))
        for x, y in mesh.nodes:
            inside_hole = config.hole_x_min < x < config.hole_x_max and config.hole_y_min < y < config.hole_y_max
            self.assertFalse(inside_hole)

    def test_boundary_node_sets_match_coarse_expectations(self) -> None:
        mesh = generate_mesh(ProblemConfig(), MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1))
        self.assertEqual(len(mesh.boundary_nodes["top"]), 3)
        self.assertEqual(len(mesh.boundary_nodes["bottom"]), 3)
        self.assertEqual(len(mesh.boundary_nodes["left"]), 3)
        self.assertEqual(len(mesh.boundary_nodes["right"]), 3)
        self.assertEqual(len(mesh.boundary_nodes["hole_top"]), 3)
        self.assertEqual(len(mesh.boundary_nodes["hole_bottom"]), 3)
        self.assertEqual(len(mesh.boundary_nodes["hole_left"]), 3)
        self.assertEqual(len(mesh.boundary_nodes["hole_right"]), 3)

    def test_boundary_edge_sets_match_patch_layout(self) -> None:
        mesh = generate_mesh(ProblemConfig(), MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1))
        self.assertEqual(len(mesh.boundary_edges["top"]), 1)
        self.assertEqual(len(mesh.boundary_edges["bottom"]), 1)
        self.assertEqual(len(mesh.boundary_edges["left"]), 1)
        self.assertEqual(len(mesh.boundary_edges["right"]), 1)
        self.assertEqual(len(mesh.boundary_edges["hole_top"]), 1)
        self.assertEqual(len(mesh.boundary_edges["hole_bottom"]), 1)
        self.assertEqual(len(mesh.boundary_edges["hole_left"]), 1)
        self.assertEqual(len(mesh.boundary_edges["hole_right"]), 1)

    def test_coarse_mesh_uses_four_named_patches(self) -> None:
        mesh = generate_mesh(ProblemConfig(), MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1))
        self.assertEqual({element.patch_name for element in mesh.elements}, {"top", "right", "bottom", "left"})

    def test_refinement_increases_node_and_element_count(self) -> None:
        config = ProblemConfig()
        coarse = generate_mesh(config, MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1))
        fine = generate_mesh(config, MeshSpec(nx_side=2, nx_hole=2, ny_side=2, ny_hole=2))
        self.assertGreater(len(fine.nodes), len(coarse.nodes))
        self.assertGreater(len(fine.elements), len(coarse.elements))

    def test_mismatched_side_subdivision_raises(self) -> None:
        with self.assertRaises(ValueError):
            MeshSpec(nx_side=5, nx_hole=1, ny_side=4, ny_hole=1)

    def test_corner_connector_has_unique_nodes_when_conforming(self) -> None:
        """Bottom/left share edge (0,0)-(hole_x_min,hole_y_min); one node per parametric station."""
        config = ProblemConfig()
        n = 3
        mesh = generate_mesh(config, MeshSpec(nx_side=n, nx_hole=2, ny_side=n, ny_hole=2))
        x0, y0 = 0.0, 0.0
        x1, y1 = config.hole_x_min, config.hole_y_min
        on_segment = []
        for node_id, (x, y) in enumerate(mesh.nodes):
            dx, dy = x - x0, y - y0
            ex, ey = x1 - x0, y1 - y0
            cross = abs(dx * ey - dy * ex)
            if cross > 1e-6 * max(abs(x1), abs(y1), 1.0):
                continue
            if not (-1e-6 <= x <= x1 + 1e-6 and -1e-6 <= y <= y1 + 1e-6):
                continue
            on_segment.append(node_id)
        self.assertEqual(len(on_segment), 2 * n + 1)


if __name__ == "__main__":
    unittest.main()
