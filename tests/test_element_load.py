from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from element.b_matrix import bending_B_matrix, shear_B_matrix
from element.heterosis import heterosis_element_edge_load_vector


def _rect_xy(width: float, height: float) -> np.ndarray:
    return np.array(
        [
            [0.0, 0.0],
            [width, 0.0],
            [width, height],
            [0.0, height],
            [width / 2.0, 0.0],
            [width, height / 2.0],
            [width / 2.0, height],
            [0.0, height / 2.0],
        ],
        dtype=float,
    )


class ElementEdgeLoadTests(unittest.TestCase):
    def test_constant_line_load_total_matches_analytic(self) -> None:
        w, h = 2.0, 1.0
        xy = _rect_xy(w, h)
        q = 3.0
        fe = heterosis_element_edge_load_vector(xy, local_edge_index=2, line_load_w=q)
        self.assertAlmostEqual(float(np.sum(fe[8:])), 0.0, places=14)
        self.assertAlmostEqual(float(np.sum(fe[:8])), q * w, places=10)

    def test_bottom_edge_length(self) -> None:
        w, h = 4.0, 2.5
        xy = _rect_xy(w, h)
        q = 1.25
        fe = heterosis_element_edge_load_vector(xy, local_edge_index=0, line_load_w=q)
        self.assertAlmostEqual(float(np.sum(fe[:8])), q * w, places=10)

    def test_invalid_edge_raises(self) -> None:
        xy = _rect_xy(1.0, 1.0)
        with self.assertRaises(ValueError):
            heterosis_element_edge_load_vector(xy, local_edge_index=5, line_load_w=1.0)


class BMatrixTests(unittest.TestCase):
    def test_b_matrix_shapes_and_positive_jacobian(self) -> None:
        xy = _rect_xy(2.0, 1.0)
        bb, det_b = bending_B_matrix(0.1, -0.2, xy)
        bs, det_s = shear_B_matrix(-0.3, 0.4, xy)
        self.assertEqual(bb.shape, (3, 26))
        self.assertEqual(bs.shape, (2, 26))
        self.assertGreater(det_b, 0.0)
        self.assertGreater(det_s, 0.0)


if __name__ == "__main__":
    unittest.main()
