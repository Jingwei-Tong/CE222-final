from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from config import ProblemConfig
from mesh import MeshSpec

if TYPE_CHECKING:
    from solver.model_runner import ModelRunResult


@dataclass(frozen=True)
class ConvergenceRow:
    label: str
    spec: MeshSpec
    num_nodes: int
    num_elements: int
    num_dof: int
    point_A_deflection: float


@dataclass(frozen=True)
class ConvergenceSeries:
    config: ProblemConfig
    rows: tuple[ConvergenceRow, ...]


def run_convergence_series(
    config: ProblemConfig,
    refinement_list: list[MeshSpec] | tuple[MeshSpec, ...],
) -> ConvergenceSeries:
    if len(refinement_list) == 0:
        raise ValueError("refinement_list must contain at least one MeshSpec.")

    rows: list[ConvergenceRow] = []
    for spec in refinement_list:
        from solver.model_runner import run_model

        result: ModelRunResult = run_model(config, spec)
        rows.append(
            ConvergenceRow(
                label=_spec_label(spec),
                spec=spec,
                num_nodes=len(result.mesh.nodes),
                num_elements=len(result.mesh.elements),
                num_dof=result.dof_map_num_dof,
                point_A_deflection=result.point_A_deflection,
            )
        )
    return ConvergenceSeries(config=config, rows=tuple(rows))


def format_convergence_table(series: ConvergenceSeries) -> str:
    headers = ("label", "nodes", "elements", "dof", "w(A)")
    body = [
        (
            row.label,
            str(row.num_nodes),
            str(row.num_elements),
            str(row.num_dof),
            f"{row.point_A_deflection:.8e}",
        )
        for row in series.rows
    ]
    widths = [len(h) for h in headers]
    for line in body:
        widths = [max(w, len(cell)) for w, cell in zip(widths, line)]

    def fmt(line: tuple[str, ...]) -> str:
        return " | ".join(cell.ljust(width) for cell, width in zip(line, widths))

    separator = "-+-".join("-" * width for width in widths)
    lines = [fmt(headers), separator]
    lines.extend(fmt(line) for line in body)
    return "\n".join(lines)


def _spec_label(spec: MeshSpec) -> str:
    return (
        f"side{spec.nx_side}"
        f"_holex{spec.nx_hole}"
        f"_holey{spec.ny_hole}"
    )
