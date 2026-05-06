from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import ProblemConfig
from mesh import StructuredPatchMesh


PATCH_COLORS = {
    "top": "#fcf8e3",
    "right": "#eadcf8",
    "bottom": "#dff0d8",
    "left": "#d9edf7",
}


def plot_mesh(
    mesh: StructuredPatchMesh,
    config: ProblemConfig,
    show_node_ids: bool = False,
    show_element_ids: bool = False,
    save_path: str | Path | None = None,
):
    fig, ax = _base_figure(config)
    _draw_all_elements(ax, mesh, color="#2f6fed", linewidth=0.9)
    _draw_point_a(ax, config)

    if show_node_ids:
        for node_id, (x, y) in enumerate(mesh.nodes):
            ax.text(x, y, str(node_id), fontsize=7, color="#444444")

    if show_element_ids:
        for element in mesh.elements:
            cx, cy = _element_center(mesh, element.q8_nodes)
            ax.text(cx, cy, str(element.element_id), fontsize=8, color="#111111")

    ax.set_title("Structured Patch Mesh")
    _finalize_axes(ax, config)
    _maybe_save(fig, save_path)
    return fig, ax


def plot_patch_layout(
    mesh: StructuredPatchMesh,
    config: ProblemConfig,
    save_path: str | Path | None = None,
):
    fig, ax = _base_figure(config)

    for element in mesh.elements:
        xs, ys = _element_polygon(mesh, element.q8_nodes)
        color = PATCH_COLORS.get(element.patch_name, "#eeeeee")
        ax.fill(xs, ys, facecolor=color, edgecolor="#666666", linewidth=0.8, alpha=0.85)

    _draw_point_a(ax, config)
    ax.set_title("Patch Layout")
    _finalize_axes(ax, config)
    _maybe_save(fig, save_path)
    return fig, ax


def plot_boundary_nodes(
    mesh: StructuredPatchMesh,
    config: ProblemConfig,
    boundary_name: str,
    save_path: str | Path | None = None,
):
    fig, ax = _base_figure(config)
    _draw_all_elements(ax, mesh, color="#bbbbbb", linewidth=0.7)

    node_ids = mesh.boundary_nodes[boundary_name]
    xs = [mesh.nodes[node_id][0] for node_id in node_ids]
    ys = [mesh.nodes[node_id][1] for node_id in node_ids]
    ax.scatter(xs, ys, s=30, color="#d62728", zorder=4, label=boundary_name)

    _draw_point_a(ax, config)
    ax.legend(loc="best")
    ax.set_title(f"Boundary Nodes: {boundary_name}")
    _finalize_axes(ax, config)
    _maybe_save(fig, save_path)
    return fig, ax


def plot_boundary_edges(
    mesh: StructuredPatchMesh,
    config: ProblemConfig,
    boundary_name: str,
    save_path: str | Path | None = None,
):
    fig, ax = _base_figure(config)
    _draw_all_elements(ax, mesh, color="#cccccc", linewidth=0.7)

    for edge in mesh.boundary_edges[boundary_name]:
        xs = [mesh.nodes[node_id][0] for node_id in edge.q8_nodes]
        ys = [mesh.nodes[node_id][1] for node_id in edge.q8_nodes]
        ax.plot(xs, ys, color="#d62728", linewidth=2.2, zorder=4)

    _draw_point_a(ax, config)
    ax.set_title(f"Boundary Edges: {boundary_name}")
    _finalize_axes(ax, config)
    _maybe_save(fig, save_path)
    return fig, ax


def _base_figure(config: ProblemConfig):
    fig, ax = plt.subplots(figsize=(9, 5.4))
    outer_x = [0.0, config.outer_width, config.outer_width, 0.0, 0.0]
    outer_y = [0.0, 0.0, config.outer_height, config.outer_height, 0.0]
    hole_x = [
        config.hole_x_min,
        config.hole_x_max,
        config.hole_x_max,
        config.hole_x_min,
        config.hole_x_min,
    ]
    hole_y = [
        config.hole_y_min,
        config.hole_y_min,
        config.hole_y_max,
        config.hole_y_max,
        config.hole_y_min,
    ]
    ax.plot(outer_x, outer_y, color="#1f1f1f", linewidth=1.8)
    ax.plot(hole_x, hole_y, color="#1f1f1f", linewidth=1.8)
    return fig, ax


def _draw_all_elements(ax, mesh: StructuredPatchMesh, color: str, linewidth: float) -> None:
    for element in mesh.elements:
        xs, ys = _element_polygon(mesh, element.q8_nodes)
        ax.plot(xs, ys, color=color, linewidth=linewidth)


def _draw_point_a(ax, config: ProblemConfig) -> None:
    x_a, y_a = config.point_A_coordinates
    ax.scatter([x_a], [y_a], color="#111111", s=45, zorder=5)
    ax.text(x_a, y_a, "  A", fontsize=10, color="#111111", va="bottom")


def _element_polygon(mesh: StructuredPatchMesh, q8_nodes: tuple[int, ...]) -> tuple[list[float], list[float]]:
    order = [0, 4, 1, 5, 2, 6, 3, 7, 0]
    xs = [mesh.nodes[q8_nodes[i]][0] for i in order]
    ys = [mesh.nodes[q8_nodes[i]][1] for i in order]
    return xs, ys


def _element_center(mesh: StructuredPatchMesh, q8_nodes: tuple[int, ...]) -> tuple[float, float]:
    corner_ids = q8_nodes[:4]
    xs = [mesh.nodes[node_id][0] for node_id in corner_ids]
    ys = [mesh.nodes[node_id][1] for node_id in corner_ids]
    return sum(xs) / 4.0, sum(ys) / 4.0


def _finalize_axes(ax, config: ProblemConfig) -> None:
    pad_x = 0.03 * config.outer_width
    pad_y = 0.03 * config.outer_height
    ax.set_xlim(-pad_x, config.outer_width + pad_x)
    ax.set_ylim(-pad_y, config.outer_height + pad_y)
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, linestyle=":", linewidth=0.6)


def _maybe_save(fig, save_path: str | Path | None) -> None:
    if save_path is not None:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=180, bbox_inches="tight")
