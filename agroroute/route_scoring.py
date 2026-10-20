"""Multi-factor scoring utilities for candidate rover routes."""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class RouteScore:
    route_index: int
    distance_score: float
    coverage_score: float
    battery_score: float
    safety_score: float
    total_score: float

    def to_dict(self) -> dict:
        return asdict(self)


def score_route(
    route_index: int,
    steps: int,
    coverage_pct: float,
    battery_remaining: float,
    safe: bool,
) -> RouteScore:
    """Score one candidate route using normalized mission factors."""

    if steps < 0:
        raise ValueError("Route steps cannot be negative.")
    if not 0 <= coverage_pct <= 100:
        raise ValueError("Coverage must be between 0 and 100.")
    if not 0 <= battery_remaining <= 100:
        raise ValueError("Battery must be between 0 and 100.")

    distance_score = round(100 / (1 + steps) * 10, 2)
    distance_score = min(100.0, distance_score)

    coverage_score = round(coverage_pct, 2)
    battery_score = round(battery_remaining, 2)
    safety_score = 100.0 if safe else 0.0

    total = (
        distance_score * 0.25
        + coverage_score * 0.30
        + battery_score * 0.20
        + safety_score * 0.25
    )

    return RouteScore(
        route_index=route_index,
        distance_score=distance_score,
        coverage_score=coverage_score,
        battery_score=battery_score,
        safety_score=safety_score,
        total_score=round(total, 2),
    )


def rank_routes(routes: list[RouteScore]) -> list[RouteScore]:
    """Return candidate routes ranked from strongest to weakest."""

    return sorted(
        routes,
        key=lambda route: (
            route.total_score,
            route.coverage_score,
            route.battery_score,
            -route.route_index,
        ),
        reverse=True,
    )