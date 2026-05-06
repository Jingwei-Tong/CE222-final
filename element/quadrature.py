from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GaussPoint2D:
    xi: float
    eta: float
    weight: float


def gauss_1d(order: int) -> tuple[tuple[float, float], ...]:
    if order == 2:
        a = 1.0 / 3.0**0.5
        return ((-a, 1.0), (a, 1.0))
    if order == 3:
        a = (3.0 / 5.0) ** 0.5
        return ((-a, 5.0 / 9.0), (0.0, 8.0 / 9.0), (a, 5.0 / 9.0))
    raise ValueError(f"Unsupported 1D Gauss order: {order}")


def gauss_tensor_2d(order: int) -> tuple[GaussPoint2D, ...]:
    pts1d = gauss_1d(order)
    return tuple(
        GaussPoint2D(xi=float(xi), eta=float(eta), weight=float(wx * wy))
        for xi, wx in pts1d
        for eta, wy in pts1d
    )


def gauss_2x2() -> tuple[GaussPoint2D, ...]:
    return gauss_tensor_2d(2)


def gauss_3x3() -> tuple[GaussPoint2D, ...]:
    return gauss_tensor_2d(3)
