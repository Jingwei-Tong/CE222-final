from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib.tri import Triangulation

from assembly import build_dof_map
from post.convergence import ConvergenceSeries

if TYPE_CHECKING:
    from solver.model_runner import ModelRunResult


def plot_convergence_deflection(
    series: ConvergenceSeries,
    save_path: str | Path | None = None,
):
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    x = [row.num_elements for row in series.rows]
    y = [row.point_A_deflection for row in series.rows]

    ax.plot(x, y, marker="o", linewidth=1.5, color="#2f6fed")
    ax.set_xlabel("Number of elements")
    ax.set_ylabel("Deflection at A")
    ax.set_title("Convergence of Point A Deflection")
    ax.grid(True, linestyle=":", linewidth=0.6)

    if save_path is not None:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=180, bbox_inches="tight")

    return fig, ax


def plot_deflection_surface_3d(
    model_result: ModelRunResult,
    save_path: str | Path | None = None,
    z_scale: float | None = None,
):
    x, y, z, triangles = _surface_mesh_data(model_result)
    z_scale = _auto_z_scale(x, y, z) if z_scale is None else z_scale
    z_plot = z * z_scale
    triangulation = Triangulation(x, y, np.array(triangles, dtype=int))

    fig = plt.figure(figsize=(8.0, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_trisurf(
        triangulation,
        z_plot,
        cmap="turbo",
        linewidth=0.0,
        edgecolor="none",
        antialiased=True,
        shade=False,
    )
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("w")
    ax.set_title(f"3D Deflection Surface (x{z_scale:.1f} scale)")
    ax.view_init(elev=30, azim=-55)
    fig.colorbar(surf, ax=ax, shrink=0.7, pad=0.1, label="scaled w")

    if save_path is not None:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=180, bbox_inches="tight")

    return fig, ax


def write_interactive_deflection_surface_html(
    model_result: ModelRunResult,
    save_path: str | Path,
    z_scale: float | None = None,
) -> Path:
    x, y, z, triangles = _surface_mesh_data(model_result)
    z_scale = _auto_z_scale(x, y, z) if z_scale is None else z_scale
    z_plot = (z * z_scale).tolist()

    i_vals = [tri[0] for tri in triangles]
    j_vals = [tri[1] for tri in triangles]
    k_vals = [tri[2] for tri in triangles]

    payload = {
        "x": x.tolist(),
        "y": y.tolist(),
        "z": z_plot,
        "i": i_vals,
        "j": j_vals,
        "k": k_vals,
        "title": f"Interactive 3D Deflection Surface (x{z_scale:.1f} scale)",
    }

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{payload["title"]}</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; background: #ffffff; }}
    #plot {{ width: 100vw; height: 100vh; }}
  </style>
</head>
<body>
  <div id="plot"></div>
  <script>
    const data = {json.dumps(payload)};
    const mesh = {{
      type: "mesh3d",
      x: data.x,
      y: data.y,
      z: data.z,
      i: data.i,
      j: data.j,
      k: data.k,
      intensity: data.z,
      colorscale: "Turbo",
      colorbar: {{ title: "scaled w" }},
      flatshading: false,
      opacity: 1.0
    }};
    const nodes = {{
      type: "scatter3d",
      mode: "markers",
      x: data.x,
      y: data.y,
      z: data.z,
      marker: {{ size: 2.5, color: "black", opacity: 0.35 }},
      showlegend: false
    }};
    const layout = {{
      title: data.title,
      margin: {{ l: 0, r: 0, b: 0, t: 48 }},
      scene: {{
        xaxis: {{ title: "x" }},
        yaxis: {{ title: "y" }},
        zaxis: {{ title: "w" }},
        camera: {{ eye: {{ x: 1.6, y: -1.6, z: 1.1 }} }}
      }}
    }};
    Plotly.newPlot("plot", [mesh, nodes], layout, {{responsive: true}});
  </script>
</body>
</html>
"""

    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path


def plot_deflection_contour(
    model_result: ModelRunResult,
    save_path: str | Path | None = None,
):
    mesh = model_result.mesh
    dof_map = build_dof_map(mesh)

    w_nodes = dof_map.w_nodes
    x = np.array([mesh.nodes[node_id][0] for node_id in w_nodes], dtype=float)
    y = np.array([mesh.nodes[node_id][1] for node_id in w_nodes], dtype=float)
    z = np.array([model_result.u_full[dof_map.w_dof(node_id)] for node_id in w_nodes], dtype=float)
    node_lookup = {node_id: i for i, node_id in enumerate(w_nodes)}

    triangles: list[tuple[int, int, int]] = []
    for element in mesh.elements:
        n0, n1, n2, n3 = element.q8_nodes[:4]
        triangles.append((node_lookup[n0], node_lookup[n1], node_lookup[n2]))
        triangles.append((node_lookup[n0], node_lookup[n2], node_lookup[n3]))

    triangulation = Triangulation(x, y, np.array(triangles, dtype=int))

    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    contour = ax.tricontourf(triangulation, z, levels=18, cmap="turbo")
    ax.triplot(triangulation, color="white", linewidth=0.25, alpha=0.35)
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Deflection Contour")
    fig.colorbar(contour, ax=ax, shrink=0.85, pad=0.02, label="w")

    if save_path is not None:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=180, bbox_inches="tight")

    return fig, ax


def _auto_z_scale(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
    xy_span = max(float(x.max() - x.min()), float(y.max() - y.min()), 1.0)
    z_span = max(float(np.max(np.abs(z))), 1e-12)
    return 0.15 * xy_span / z_span


def _surface_mesh_data(
    model_result: ModelRunResult,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[tuple[int, int, int]]]:
    mesh = model_result.mesh
    dof_map = build_dof_map(mesh)

    w_nodes = dof_map.w_nodes
    x = np.array([mesh.nodes[node_id][0] for node_id in w_nodes], dtype=float)
    y = np.array([mesh.nodes[node_id][1] for node_id in w_nodes], dtype=float)
    z = np.array([model_result.u_full[dof_map.w_dof(node_id)] for node_id in w_nodes], dtype=float)
    node_lookup = {node_id: i for i, node_id in enumerate(w_nodes)}

    triangles: list[tuple[int, int, int]] = []
    for element in mesh.elements:
        n0, n1, n2, n3 = element.q8_nodes[:4]
        triangles.append((node_lookup[n0], node_lookup[n1], node_lookup[n2]))
        triangles.append((node_lookup[n0], node_lookup[n2], node_lookup[n3]))

    return x, y, z, triangles
