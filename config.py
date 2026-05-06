from __future__ import annotations

from dataclasses import dataclass


VALID_EDGES = (
    "left",
    "right",
    "top",
    "bottom",
    "hole_left",
    "hole_right",
    "hole_top",
    "hole_bottom",
)


@dataclass(frozen=True)
class ProblemConfig:
    """Minimal project configuration for the CE222 option-1 plate problem."""

    outer_width: float = 500.0
    outer_height: float = 300.0

    cutout_width: float = 250.0
    cutout_height: float = 180.0

    young_modulus: float = 200.0
    poisson_ratio: float = 0.25
    thickness: float = 20.0

    applied_shear: float = 1.0
    clamped_edges: tuple[str, ...] = ("left", "top")
    free_edges: tuple[str, ...] = ("right", "bottom")
    loaded_edges: tuple[str, ...] | None = ("hole_top",)

    point_A: tuple[float, float] | None = None

    def __post_init__(self) -> None:
        self._validate_dimensions()
        self._validate_material()
        self._validate_edges()
        self._validate_point_A()

    def _validate_dimensions(self) -> None:
        if self.outer_width <= 0.0 or self.outer_height <= 0.0:
            raise ValueError("Outer plate dimensions must be positive.")
        if self.cutout_width <= 0.0 or self.cutout_height <= 0.0:
            raise ValueError("Cutout dimensions must be positive.")
        if self.cutout_width >= self.outer_width or self.cutout_height >= self.outer_height:
            raise ValueError("Cutout must fit strictly inside the outer plate.")
        if self.thickness <= 0.0:
            raise ValueError("Plate thickness must be positive.")

    def _validate_material(self) -> None:
        if self.young_modulus <= 0.0:
            raise ValueError("Young's modulus must be positive.")
        if not (-1.0 < self.poisson_ratio < 0.5):
            raise ValueError("Poisson ratio must satisfy -1 < nu < 0.5.")

    def _validate_edges(self) -> None:
        edge_union = set(self.clamped_edges) | set(self.free_edges)
        if self.loaded_edges is not None:
            edge_union |= set(self.loaded_edges)
        unknown_edges = edge_union.difference(VALID_EDGES)
        if unknown_edges:
            raise ValueError(f"Unknown edge labels: {sorted(unknown_edges)}")
        if set(self.clamped_edges).intersection(self.free_edges):
            raise ValueError("An edge cannot be both clamped and free.")

    def _validate_point_A(self) -> None:
        if self.point_A is None:
            return
        x_a, y_a = self.point_A
        if not (0.0 <= x_a <= self.outer_width and 0.0 <= y_a <= self.outer_height):
            raise ValueError("Point A must lie inside the outer plate bounds.")

    @property
    def hole_x_min(self) -> float:
        return 0.5 * (self.outer_width - self.cutout_width)

    @property
    def hole_x_max(self) -> float:
        return self.hole_x_min + self.cutout_width

    @property
    def hole_y_min(self) -> float:
        return 0.5 * (self.outer_height - self.cutout_height)

    @property
    def hole_y_max(self) -> float:
        return self.hole_y_min + self.cutout_height

    @property
    def point_A_coordinates(self) -> tuple[float, float]:
        if self.point_A is not None:
            return self.point_A
        return (self.hole_x_max, self.hole_y_min)

    def as_dict(self) -> dict[str, object]:
        return {
            "outer_width": self.outer_width,
            "outer_height": self.outer_height,
            "cutout_width": self.cutout_width,
            "cutout_height": self.cutout_height,
            "young_modulus": self.young_modulus,
            "poisson_ratio": self.poisson_ratio,
            "thickness": self.thickness,
            "applied_shear": self.applied_shear,
            "clamped_edges": self.clamped_edges,
            "free_edges": self.free_edges,
            "loaded_edges": self.loaded_edges,
            "point_A": self.point_A_coordinates,
        }
