from __future__ import annotations

import os
from pathlib import Path
from pprint import pprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".mplconfig"))

from config import ProblemConfig
from mesh import MeshSpec, generate_mesh
from mesh.visualization import plot_boundary_edges, plot_boundary_nodes, plot_mesh, plot_patch_layout


def main() -> None:
    output_dir = PROJECT_ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)

    config = ProblemConfig()
    spec = MeshSpec(nx_side=5, nx_hole=7, ny_side=5, ny_hole=6)
    mesh = generate_mesh(config, spec)

    print("CONFIG")
    pprint(config.as_dict())
    print("\nMESH")
    print(f"nodes: {len(mesh.nodes)}")
    print(f"elements: {len(mesh.elements)}")
    print("boundary node counts:", {name: len(ids) for name, ids in mesh.boundary_nodes.items()})
    print("boundary edge counts:", {name: len(edges) for name, edges in mesh.boundary_edges.items()})

    figures = {
        "mesh_overview_demo.png": lambda: plot_mesh(mesh, config),
        "mesh_patch_layout_demo.png": lambda: plot_patch_layout(mesh, config),
        "mesh_boundary_nodes_left_demo.png": lambda: plot_boundary_nodes(mesh, config, "left"),
        "mesh_boundary_edges_hole_top_demo.png": lambda: plot_boundary_edges(mesh, config, "hole_top"),
    }

    print("\nWRITING FIGURES")
    for filename, plotter in figures.items():
        path = output_dir / filename
        fig, _ = plotter()
        fig.savefig(path, dpi=180, bbox_inches="tight")
        fig.clf()
        print(path)


if __name__ == "__main__":
    main()
