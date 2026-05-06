from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import sparse

from assembly import (
    apply_clamped_bc,
    assemble_global_load,
    assemble_global_stiffness,
    build_dof_map,
    clamped_dofs,
    expand_solution,
)
from config import ProblemConfig
from mesh import MeshSpec, StructuredPatchMesh, generate_mesh
from post.point_queries import query_point_A_deflection
from solver.linear_solver import LinearSolveResult, solve_system


@dataclass(frozen=True)
class ModelRunResult:
    config: ProblemConfig
    mesh: StructuredPatchMesh
    dof_map_num_dof: int
    k_full: sparse.spmatrix | np.ndarray
    f_full: np.ndarray
    constrained_dofs: np.ndarray
    free_dofs: np.ndarray
    k_reduced: sparse.spmatrix | np.ndarray
    f_reduced: np.ndarray
    solve_result: LinearSolveResult
    u_full: np.ndarray
    point_A_deflection: float


def run_model(config: ProblemConfig, spec: MeshSpec | None = None) -> ModelRunResult:
    mesh = generate_mesh(config, spec)
    dof_map = build_dof_map(mesh)

    k_full = assemble_global_stiffness(mesh, dof_map, config)
    f_full = assemble_global_load(mesh, dof_map, config)

    constrained = clamped_dofs(mesh, dof_map, config)
    k_reduced, f_reduced, free_dofs = apply_clamped_bc(k_full, f_full, constrained)
    solve_result = solve_system(k_reduced, f_reduced)
    u_full = expand_solution(solve_result.u_free, free_dofs, dof_map.num_dof)
    point_a_deflection = query_point_A_deflection(u_full, mesh, config)

    return ModelRunResult(
        config=config,
        mesh=mesh,
        dof_map_num_dof=dof_map.num_dof,
        k_full=k_full,
        f_full=f_full,
        constrained_dofs=constrained,
        free_dofs=free_dofs,
        k_reduced=k_reduced,
        f_reduced=f_reduced,
        solve_result=solve_result,
        u_full=u_full,
        point_A_deflection=point_a_deflection,
    )
