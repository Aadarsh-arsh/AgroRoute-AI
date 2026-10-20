"""Unified mission reporting for AgroRoute AI."""

from __future__ import annotations

from .farm import Farm
from .mission_analytics import analyze_mission
from .mission_control import preflight
from .treatment import build_zone_plans, priority_score


def build_mission_report(
    farm: Farm,
    path: list[tuple[int, int]],
    diagnoses: dict | None = None,
    battery: float = 100.0,
    consumption_per_step: float = 0.4,
    reserve_pct: float = 15.0,
    capacity: int = 20,
    rain: bool = False,
) -> dict:
    """Build one structured report spanning planning, safety and treatment."""

    analytics = analyze_mission(
        farm,
        path,
        battery=battery,
        consumption_per_step=consumption_per_step,
        reserve_pct=reserve_pct,
    )

    flight = preflight(
        farm,
        path,
        per_step=consumption_per_step,
        capacity=capacity,
        reserve=reserve_pct,
        battery=battery,
    )

    plans = build_zone_plans(
        farm,
        diagnoses=diagnoses,
        rain=rain,
    )

    treatments = []

    for plan in plans:
        item = plan.to_dict()
        item["priority_score"] = priority_score(plan)
        treatments.append(item)

    warnings = list(flight.issues)

    if rain:
        warnings.append("Rain conditions detected; spraying is restricted.")

    if not analytics.route_valid:
        warnings.append("Route validation failed.")

    return {
        "mission": {
            "ready": analytics.mission_ready and flight.feasible,
            "route_steps": analytics.route_steps,
            "coverage_pct": analytics.coverage_pct,
            "battery_remaining_pct": analytics.estimated_battery_remaining,
            "inspection_efficiency_pct": analytics.inspection_efficiency_pct,
        },
        "safety": {
            "preflight_feasible": flight.feasible,
            "starts_at_base": analytics.starts_at_base,
            "returns_to_base": analytics.returns_to_base,
            "route_valid": analytics.route_valid,
            "warnings": warnings,
        },
        "farm": {
            "name": farm.name,
            "rows": farm.rows,
            "cols": farm.cols,
            "infected_zones": analytics.infected_zones,
            "visited_infected_zones": analytics.visited_infected_zones,
        },
        "treatment": {
            "zones": treatments,
            "rain_mode": rain,
        },
    }