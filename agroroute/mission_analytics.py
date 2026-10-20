"""Mission analytics for virtual rover planning and execution."""

from __future__ import annotations

from dataclasses import dataclass, asdict

from .farm import Farm


@dataclass(frozen=True)
class MissionAnalytics:
    route_steps: int
    unique_cells: int
    infected_zones: int
    visited_infected_zones: int
    coverage_pct: float
    estimated_consumption_pct: float
    estimated_battery_remaining: float
    inspection_efficiency_pct: float
    starts_at_base: bool
    returns_to_base: bool
    route_valid: bool
    mission_ready: bool

    def to_dict(self) -> dict:
        return asdict(self)


def analyze_mission(
    farm: Farm,
    path: list[tuple[int, int]],
    battery: float = 100.0,
    consumption_per_step: float = 0.4,
    reserve_pct: float = 15.0,
) -> MissionAnalytics:
    """Analyze route quality, coverage, battery and mission readiness."""

    if not 0 <= battery <= 100:
        raise ValueError("Battery must be between 0 and 100.")
    if consumption_per_step < 0:
        raise ValueError("Consumption per step cannot be negative.")
    if not 0 <= reserve_pct <= 100:
        raise ValueError("Reserve must be between 0 and 100.")

    route_steps = max(0, len(path) - 1)
    unique_cells = len(set(path))

    infected = {
        (r, c)
        for r in range(farm.rows)
        for c in range(farm.cols)
        if farm.cells[r][c] == "infected"
    }

    visited_infected = infected.intersection(path)

    valid = bool(path)

    for current, nxt in zip(path, path[1:]):
        if (
            not farm.in_bounds(*current)
            or not farm.in_bounds(*nxt)
            or farm.cells[nxt[0]][nxt[1]] == "obstacle"
            or abs(current[0] - nxt[0]) + abs(current[1] - nxt[1]) != 1
        ):
            valid = False
            break

    starts_at_base = bool(path) and path[0] == farm.rover
    returns_to_base = bool(path) and path[-1] == farm.rover

    consumption = route_steps * consumption_per_step
    remaining = round(battery - consumption, 2)

    coverage = (
        round(len(visited_infected) / len(infected) * 100, 1)
        if infected
        else 100.0
    )

    efficiency = (
        round(len(visited_infected) / route_steps * 100, 1)
        if route_steps
        else 0.0
    )

    ready = (
        valid
        and starts_at_base
        and returns_to_base
        and len(visited_infected) == len(infected)
        and remaining >= reserve_pct
    )

    return MissionAnalytics(
        route_steps=route_steps,
        unique_cells=unique_cells,
        infected_zones=len(infected),
        visited_infected_zones=len(visited_infected),
        coverage_pct=coverage,
        estimated_consumption_pct=round(consumption, 2),
        estimated_battery_remaining=remaining,
        inspection_efficiency_pct=efficiency,
        starts_at_base=starts_at_base,
        returns_to_base=returns_to_base,
        route_valid=valid,
        mission_ready=ready,
    )