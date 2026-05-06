# CE222 Final Project

Develop a finite element program for the CE222 Option 1 plate-with-cutout problem. The code uses a heterosis Mindlin plate element with Q8 interpolation for transverse displacement and Q9 interpolation for rotations.

## Final Result

The final reported transverse deflection at point A is approximately:

```text
w(A) = -0.348 mm
```

The finest stored report case is the `50 x 50` refinement with `w(A) = -3.48029453e-01`, supported by an additional `80 x 80` sparse-solver check near `-3.47609000e-01`.

## Project Structure

```text
assembly/   Global stiffness, load vector, DOF map, and boundary conditions
element/    Shape functions, Jacobian, constitutive matrices, B matrices, and heterosis element routines
examples/   Final plate-with-cutout driver
mesh/       Structured patch mesh generation and mesh visualization
post/       Point queries, convergence table generation, and plotting
solver/     Linear solver and model runner
tests/      Unit and integration tests
outputs/    Report figures and final-case output table
```

## Setup

```bash
python -m pip install -r requirements.txt
```

## Run Tests

```bash
python -m unittest discover tests
```

The current suite contains 90 tests covering configuration, mesh generation, shape functions, element formulation, assembly, loading, boundary conditions, solver behavior, convergence utilities, plotting, and the final-case driver.

## Run Final Case

```bash
python examples/final_plate_with_cutout.py
```

This writes the convergence table and report figures under `outputs/final_case/`.

## Notes

- The main report draft is `CE222_Final_Report_Option1.md`.
- `Claude_Test_Report_Prompt.md` summarizes the verification tests for generating a report testing section.
- `Option1_Project_Blueprint.md` is the original project planning document.
