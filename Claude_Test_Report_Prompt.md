# Claude Prompt For Testing And Verification Report Section

Copy the prompt below into Claude to generate a polished testing and verification section for the CE222 final report. The generated section should stay faithful to the actual files and tests in this repository.

---

You are helping write the "Testing and Verification" section of a CE222 finite element programming final report.

Write a clear, professional report section explaining what tests were performed, what each group of tests verifies, and why these tests support confidence in the final finite element result. Use only the project information below. Do not invent analytical benchmarks, exact closed-form solutions, or tests that are not listed here.

## Project Context

This project implements a finite element solver for a Mindlin plate with a centered rectangular cutout. The implemented element is a heterosis plate element:

- Q8 interpolation for transverse displacement `w`
- Q9 interpolation for rotations `theta_x` and `theta_y`
- 3 x 3 Gauss quadrature for bending terms
- 2 x 2 Gauss quadrature for transverse shear terms

The final engineering quantity of interest is the transverse deflection at point A, the lower-right corner of the cutout. The final reported result is approximately:

`w(A) = -0.348 mm`

The test suite was used to verify the finite element implementation before trusting the final convergence result.

## Test Suite Summary

The project contains 17 test files under `tests/`. The full suite currently runs 90 tests successfully with:

`python -m unittest discover tests`

## Tests Performed

### Configuration Tests

File: `tests/test_config.py`

These tests verify that the cutout is centered, the material parameters match the project interpretation, point A is located at `(375 mm, 60 mm)`, custom point-A values are respected, and invalid dimensions/materials/edge names are rejected.

### Mesh Generation Tests

File: `tests/test_mesh.py`

These tests verify that the structured patch mesh has the expected coarse counts, Q8/Q9 connectivity, no nodes inside the cutout, correct outer and cutout boundary-node sets, correct boundary-edge sets, four named patches, increasing node and element counts under refinement, error handling for mismatched subdivisions, and conforming shared nodes along patch interfaces.

The mesh implementation is located in `mesh/core.py`, with the public API re-exported through `mesh/__init__.py`.

### Mesh Visualization Tests

File: `tests/test_visualization.py`

These tests verify that mesh plots, patch-layout plots, boundary-node plots, and boundary-edge plots run successfully and can save PNG output.

### Shape Function Tests

File: `tests/test_element_shapes.py`

These tests verify Q8 and Q9 partition of unity, linear completeness, Q9 quadratic monomial reproduction, nodal interpolation, and heterosis stiffness symmetry.

### Quadrature, Constitutive Matrix, Jacobian, And Element Stiffness Tests

File: `tests/test_element_core.py`

These tests verify Gauss quadrature weights and polynomial integration, error handling for unsupported quadrature orders, Mindlin bending and shear constitutive matrices, Jacobian determinant behavior, physical derivative consistency, element stiffness size and symmetry, nonzero bending/shear contributions, positive semidefinite sample contributions, and the element DOF count.

### B Matrix And Element Edge Load Tests

File: `tests/test_element_load.py`

These tests verify equivalent nodal force totals for constant line loads, element edge length calculations, invalid edge handling, and bending/shear B-matrix shapes with positive Jacobian.

### Degree-Of-Freedom Mapping Tests

File: `tests/test_dof_map.py`

These tests verify the heterosis DOF layout: Q8 nodes carry transverse displacement DOFs, Q9 nodes carry rotational DOFs, center Q9 nodes do not carry Q8 transverse displacement DOFs, and element DOF ordering matches the stiffness routine.

### Global Stiffness Assembly Tests

File: `tests/test_global_stiffness.py`

These tests verify element-coordinate extraction, global stiffness dimensions, symmetry, and nonzero entries.

### Global Load Vector Tests

File: `tests/test_load_vector.py`

These tests verify top and bottom load signs, load cancellation, the cutout `hole_top` load total, and rejection of unsupported loaded edges.

### Boundary Condition Tests

File: `tests/test_boundary_conditions.py`

These tests verify that clamped DOFs cover all three DOFs on the left and top boundaries, free and constrained DOF sets are disjoint, and the reduced solution can be expanded back into the full vector.

### Linear Solver Tests

File: `tests/test_linear_solver.py`

These tests verify dense and sparse known-system solutions and error handling for zero-size, mismatched, and singular systems.

### Model Runner Integration Tests

File: `tests/test_model_runner.py`

These tests verify the default problem setup, a complete small model run, and the zero-load zero-solution case.

### Point Query Tests

File: `tests/test_point_queries.py`

These tests verify point-node matching, nodal displacement extraction, non-nodal query errors, and consistency between direct point-query extraction and the model runner's point-A deflection.

### Convergence Tests

File: `tests/test_convergence.py`

These tests verify convergence-series generation, convergence-table formatting, and error handling for empty refinement lists. The actual engineering convergence study was performed with increasingly refined meshes up to the stored `50 x 50` report case and an additional `80 x 80` sparse-solver check.

### Shear-Locking Diagnostic Tests

File: `tests/test_shear_locking.py`

These tests verify that the point-A deflection scales approximately with `1/t^3` as thickness changes and that a full-shear-integration surrogate does not show large artificial stiffening.

### Plotting And Post-Processing Tests

File: `tests/test_plotting.py`

These tests verify that convergence plots, 3D deflection-surface plots, contour plots, and interactive HTML deflection surfaces can be generated.

### Final Case Example Tests

File: `tests/test_final_case_example.py`

These tests verify that the default refinement series is nonempty and that the final-case driver writes the expected outputs, including the convergence table.

## How To Organize The Report Section

Group the tests by purpose rather than listing every assertion one by one:

1. Problem-definition and mesh verification
2. Element-level verification
3. Assembly, loading, and boundary-condition verification
4. Solver and model-runner verification
5. Post-processing, convergence, and final-result extraction
6. Shear-locking and sensitivity-related checks

Emphasize that these tests do not prove an exact analytical solution for the cutout plate problem. Instead, they verify that the numerical implementation is internally consistent and that the final answer is supported by mesh convergence and comparison with the published reference value.

## Claims To Include

- The tests cover the finite element workflow from geometry definition through final result extraction.
- Mesh tests reduce the risk of geometry, boundary-labeling, and connectivity errors.
- Shape-function, Jacobian, B-matrix, constitutive, and stiffness tests reduce the risk of element-level formulation errors.
- Assembly, load-vector, and boundary-condition tests reduce the risk of incorrect global system construction.
- Solver tests reduce the risk of incorrect linear algebra handling.
- Point-query tests verify that the reported value at point A is extracted consistently.
- Convergence tests and final-case tests support the reported value of `w(A)`.
- The shear-locking diagnostics support the reliability of the heterosis Mindlin element implementation.

## Claims To Avoid

Do not claim:

- that there is an exact closed-form analytical solution for the final cutout plate problem;
- that the code exactly matches the professor's `0.346` value;
- that passing unit tests alone proves the final answer;
- that every possible mesh or loading case was tested.

## Suggested Report Paragraph

The finite element code was verified using a unit-test suite covering the main stages of the analysis workflow. Configuration and mesh tests confirmed that the centered cutout geometry, boundary labels, patch connectivity, Q8/Q9 element connectivity, and point-A location were generated as intended. Element-level tests checked quadrature rules, shape-function properties, Jacobian behavior, constitutive matrices, B-matrix dimensions, and stiffness-matrix symmetry. Assembly tests then verified the global stiffness matrix, degree-of-freedom map, equivalent nodal load vector, and clamped boundary-condition reduction. Solver and model-runner tests confirmed correct behavior on known small systems, zero-load cases, and complete small finite element models. Additional point-query, convergence, plotting, and final-case tests verified that the reported deflection at point A could be extracted and presented consistently. Finally, shear-locking diagnostic tests checked that the deflection scaled reasonably with plate thickness and did not show large artificial stiffening. Together with the mesh-refinement study, these tests provide evidence that the final result is numerically reliable, while the remaining difference from the published reference value is best interpreted as small modeling and discretization sensitivity rather than a major implementation error.
