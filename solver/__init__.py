from .linear_solver import LinearSolveResult, solve_system

__all__ = [
    "LinearSolveResult",
    "solve_system",
    "ModelRunResult",
    "run_model",
]


def __getattr__(name: str):
    if name in {"ModelRunResult", "run_model"}:
        from .model_runner import ModelRunResult, run_model

        return {"ModelRunResult": ModelRunResult, "run_model": run_model}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
