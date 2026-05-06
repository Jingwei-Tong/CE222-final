# Option 1 Project Blueprint

## Goal

Build a from-scratch finite element program for the CE222 final project using a single
heterosis plate element for a shear-deformable isotropic elastic plate, then use it to compute
the transverse deflection at point `A` for the plate-with-centered-cutout problem in the
assignment PDF.

## Project Outcome

The finished project should produce:

- a modular FEA codebase
- unit tests for each mathematical and assembly module
- small development/verification cases
- the final plate-with-hole analysis
- a mesh convergence study for point `A`
- report-ready figures, tables, and logs

## Recommended Project Structure

```text
final222/
  Final-222-2026-1.pdf
  Option1_Project_Blueprint.md
  requirements.txt
  README.md

  config/
    problem_case.py
    material.py

  mesh/
    node.py
    element_connectivity.py
    geometry_utils.py
    mesh_generator.py

  element/
    quadrature.py
    shape_q8.py
    shape_q9.py
    jacobian.py
    constitutive.py
    b_matrix.py
    heterosis_element.py

  assembly/
    dof_map.py
    global_stiffness.py
    load_vector.py
    boundary_conditions.py

  solver/
    linear_solver.py
    model_runner.py

  post/
    point_queries.py
    field_recovery.py
    convergence.py
    plotting.py

  examples/
    patch_test_case.py
    simple_rectangular_plate.py
    final_plate_with_cutout.py

  tests/
    test_shape_q8.py
    test_shape_q9.py
    test_quadrature.py
    test_jacobian.py
    test_constitutive.py
    test_b_matrix.py
    test_element_stiffness.py
    test_mesh_generator.py
    test_dof_map.py
    test_boundary_conditions.py
    test_load_vector.py
    test_patch_cases.py
    test_end_to_end_small_case.py
```

## Module Blueprint

### 1. `config`

Purpose:

- store geometry, material, thickness, boundary condition, and loading parameters
- define point `A`
- isolate problem data from solver logic

Must support:

- outer plate dimensions
- centered cutout dimensions
- isotropic material constants `E` and `nu`
- thickness `t`
- applied edge shear
- clamped and free boundary flags

Independent tests:

- geometry values load correctly
- cutout is centered
- point `A` is placed consistently

### 2. `mesh`

Purpose:

- generate nodes and element connectivity
- identify outer and inner boundaries
- support refinement studies

Must support:

- quadratic element-compatible node layouts
- connectivity for `Q8` displacement nodes
- connectivity for `Q9` rotation nodes
- boundary node extraction by edge name

Independent tests:

- node count for a given refinement
- element count for a given refinement
- correct local node ordering
- centered cutout geometry
- correct boundary node sets

### 3. `element`

Purpose:

- contain all heterosis element mathematics

Submodules:

- `quadrature.py`: `2x2` and `3x3` Gauss rules
- `shape_q8.py`: `Q8` shape functions and derivatives
- `shape_q9.py`: `Q9` shape functions and derivatives
- `jacobian.py`: mapping and derivative transformation
- `constitutive.py`: Mindlin plate bending and shear constitutive matrices
- `b_matrix.py`: bending and shear `B` matrices
- `heterosis_element.py`: element stiffness and element load contributions

Independent tests:

- partition of unity for `Q8` and `Q9`
- nodal interpolation property
- exact integration of low-order polynomials
- positive Jacobian for valid elements
- symmetric constitutive matrices
- correct matrix dimensions
- symmetric element stiffness matrix
- consistent response for simple test fields

### 4. `assembly`

Purpose:

- map local element matrices to the global system
- apply loads and essential boundary conditions

Submodules:

- `dof_map.py`: global indexing for `w`, `theta_x`, `theta_y`
- `global_stiffness.py`: assemble `K`
- `load_vector.py`: build global `F`
- `boundary_conditions.py`: constrain clamped edges

Independent tests:

- DOF numbering is unique and complete
- assembled matrix size is correct
- assembled matrix remains symmetric
- load totals match expected edge load
- clamped edges constrain all required DOFs

### 5. `solver`

Purpose:

- solve the linear system and package results

Submodules:

- `linear_solver.py`: solve reduced system
- `model_runner.py`: orchestrate the full workflow

Independent tests:

- known small linear systems solve correctly
- reduced system residual is small
- end-to-end small model runs without failure

### 6. `post`

Purpose:

- extract engineering quantities for the report

Submodules:

- `point_queries.py`: evaluate deflection at point `A`
- `field_recovery.py`: recover strains, moments, and shear quantities
- `convergence.py`: automate mesh refinement runs
- `plotting.py`: generate plots and tables

Independent tests:

- point query returns exact nodal value when applicable
- convergence table writes correct columns
- plots run without crashing on valid results

## Test Philosophy

Each module should be testable without running the full project.

Test levels:

1. Pure math tests
- shape functions
- quadrature
- Jacobian
- constitutive matrices

2. Element tests
- `B` matrices
- element stiffness symmetry
- simple consistency checks

3. Assembly tests
- DOF map
- global stiffness assembly
- load vector
- boundary condition application

4. End-to-end tests
- small rectangular plate
- patch-style development case
- final plate-with-cutout model

## Minimum Function Interface Plan

Suggested core functions:

```python
# quadrature.py
gauss_rule_2x2()
gauss_rule_3x3()

# shape_q8.py
shape_q8(xi, eta)
dshape_q8(xi, eta)

# shape_q9.py
shape_q9(xi, eta)
dshape_q9(xi, eta)

# jacobian.py
compute_jacobian(node_coords, dN_dxi)
map_derivatives_to_physical(invJ, dN_dxi)

# constitutive.py
bending_matrix(E, nu, t)
shear_matrix(E, nu, t, kappa)

# b_matrix.py
bending_B_matrix(dN_rot_dx)
shear_B_matrix(dN_w_dx, N_rot)

# heterosis_element.py
element_stiffness(node_coords_q8, node_coords_q9, material)
element_load_vector(...)

# mesh_generator.py
generate_plate_with_center_cutout_mesh(params, refinement)

# dof_map.py
build_dof_map(mesh)

# global_stiffness.py
assemble_global_stiffness(mesh, dof_map, material)

# load_vector.py
assemble_global_load(mesh, dof_map, load_data)

# boundary_conditions.py
apply_clamped_bc(K, F, dof_map, boundary_nodes)

# linear_solver.py
solve_system(K, F)

# point_queries.py
query_point_deflection(solution, mesh, point)

# convergence.py
run_convergence_series(problem_config, refinement_list)
```

## Recommended Development Order

Build in this order:

1. `quadrature`
2. `shape_q8`
3. `shape_q9`
4. `jacobian`
5. `constitutive`
6. `b_matrix`
7. `heterosis_element`
8. `mesh_generator`
9. `dof_map`
10. `global_stiffness`
11. `load_vector`
12. `boundary_conditions`
13. `linear_solver`
14. `model_runner`
15. `point_queries`
16. `convergence`
17. `plotting`

Reason:

- the mathematical foundation is verified first
- the single element is trusted before global assembly
- the final engineering model is only attempted after all lower-level tests pass

## Verification Cases You Should Include

Before the final plate-with-cutout analysis, prepare these checks:

- shape-function interpolation checks for `Q8` and `Q9`
- Gauss integration accuracy checks
- Jacobian positivity check on undistorted and mildly distorted elements
- element stiffness symmetry check
- simple zero-strain or constant-field consistency check
- small rectangular plate smoke test
- boundary load total-force consistency check
- mesh refinement study for the final geometry

## Final Analysis Workflow

```text
ProblemConfig
  -> MeshGenerator
  -> ElementStiffness + ElementLoad
  -> GlobalAssembly
  -> BoundaryConditions
  -> LinearSolve
  -> PointAQuery
  -> ConvergenceStudy
  -> ReportFiguresAndTables
```

## Report Mapping

Suggested mapping from code to report:

- theory section:
  - `shape_q8`, `shape_q9`, `constitutive`, `b_matrix`
- modeling approach:
  - `mesh_generator`, `boundary_conditions`, `load_vector`
- development verification:
  - unit tests and patch cases
- results and accuracy:
  - final case results and convergence study
- appendices:
  - input files, auxiliary cases, raw output tables

## Immediate Next Step

Before coding the full project, define:

- the exact local node ordering for `Q8` and `Q9`
- the exact sign convention for `theta_x`, `theta_y`, shear terms, and edge loads
- the exact location of point `A` from the assignment figure
- the exact edges that are clamped or loaded in the final geometry

If these conventions are fixed early, the rest of the code and tests can remain consistent.
