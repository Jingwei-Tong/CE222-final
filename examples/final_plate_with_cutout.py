from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".mplconfig"))

from config import ProblemConfig
from mesh import MeshSpec
from post import (
    format_convergence_table,
    plot_convergence_deflection,
    plot_deflection_contour,
    plot_deflection_surface_3d,
    run_convergence_series,
    write_interactive_deflection_surface_html,
)
from solver.model_runner import ModelRunResult, run_model


@dataclass(frozen=True)
class FinalCaseArtifacts:
    model_result: ModelRunResult
    convergence_table: str
    table_path: Path
    plot_path: Path
    surface_plot_path: Path
    contour_plot_path: Path
    interactive_surface_path: Path


def default_refinement_series() -> tuple[MeshSpec, ...]:
    return (
        MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1),
        MeshSpec(nx_side=2, nx_hole=2, ny_side=2, ny_hole=2),
        MeshSpec(nx_side=3, nx_hole=3, ny_side=3, ny_hole=3),
        MeshSpec(nx_side=4, nx_hole=4, ny_side=4, ny_hole=4),
        MeshSpec(nx_side=5, nx_hole=5, ny_side=5, ny_hole=5),
        MeshSpec(nx_side=6, nx_hole=6, ny_side=6, ny_hole=6),
        MeshSpec(nx_side=8, nx_hole=8, ny_side=8, ny_hole=8),
        MeshSpec(nx_side=10, nx_hole=10, ny_side=10, ny_hole=10),
        MeshSpec(nx_side=12, nx_hole=12, ny_side=12, ny_hole=12),
        MeshSpec(nx_side=14, nx_hole=14, ny_side=14, ny_hole=14),
        MeshSpec(nx_side=16, nx_hole=16, ny_side=16, ny_hole=16),
    )


def report_refinement_series() -> tuple[MeshSpec, ...]:
    return (
        MeshSpec(nx_side=1, nx_hole=1, ny_side=1, ny_hole=1),
        MeshSpec(nx_side=2, nx_hole=2, ny_side=2, ny_hole=2),
        MeshSpec(nx_side=4, nx_hole=4, ny_side=4, ny_hole=4),
        MeshSpec(nx_side=8, nx_hole=8, ny_side=8, ny_hole=8),
        MeshSpec(nx_side=16, nx_hole=16, ny_side=16, ny_hole=16),
        MeshSpec(nx_side=30, nx_hole=30, ny_side=30, ny_hole=30),
        MeshSpec(nx_side=50, nx_hole=50, ny_side=50, ny_hole=50),
    )


def run_final_case(
    output_dir: str | Path | None = None,
    refinement_series: tuple[MeshSpec, ...] | None = None,
) -> FinalCaseArtifacts:
    project_root = Path(__file__).resolve().parents[1]
    out_dir = Path(output_dir) if output_dir is not None else project_root / "outputs" / "final_case"
    out_dir.mkdir(parents=True, exist_ok=True)

    config = ProblemConfig()
    refinement_series = refinement_series or default_refinement_series()
    final_spec = refinement_series[-1]
    model_result = run_model(config, final_spec)

    convergence = run_convergence_series(config, refinement_series)
    table = format_convergence_table(convergence)

    table_path = out_dir / "convergence_table.txt"
    table_path.write_text(table + "\n", encoding="utf-8")

    plot_path = out_dir / "convergence_point_A.png"
    fig, _ = plot_convergence_deflection(convergence, save_path=plot_path)
    fig.clf()

    surface_plot_path = out_dir / "deflection_surface_3d.png"
    fig3d, _ = plot_deflection_surface_3d(model_result, save_path=surface_plot_path)
    fig3d.clf()

    contour_plot_path = out_dir / "deflection_contour.png"
    fig2d, _ = plot_deflection_contour(model_result, save_path=contour_plot_path)
    fig2d.clf()

    interactive_surface_path = out_dir / "deflection_surface_interactive.html"
    write_interactive_deflection_surface_html(model_result, interactive_surface_path)

    return FinalCaseArtifacts(
        model_result=model_result,
        convergence_table=table,
        table_path=table_path,
        plot_path=plot_path,
        surface_plot_path=surface_plot_path,
        contour_plot_path=contour_plot_path,
        interactive_surface_path=interactive_surface_path,
    )


def main() -> None:
    artifacts = run_final_case(refinement_series=report_refinement_series())
    print("FINAL CASE COMPLETE")
    print(f"Point A deflection: {artifacts.model_result.point_A_deflection:.8e}")
    print("\nCONVERGENCE TABLE")
    print(artifacts.convergence_table)
    print(f"\nSaved table: {artifacts.table_path}")
    print(f"Saved plot: {artifacts.plot_path}")
    print(f"Saved 3D surface: {artifacts.surface_plot_path}")
    print(f"Saved contour: {artifacts.contour_plot_path}")
    print(f"Saved interactive surface: {artifacts.interactive_surface_path}")


if __name__ == "__main__":
    main()
