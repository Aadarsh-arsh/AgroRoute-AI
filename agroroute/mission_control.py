"""Pure mission preflight checks for simulated return-to-base rover missions."""
from dataclasses import dataclass
from math import isfinite
from .farm import Farm

@dataclass(frozen=True)
class Preflight:
    feasible: bool
    steps: int
    estimated_battery_end: float
    issues: tuple[str, ...]


def preflight(farm: Farm, path: list[tuple[int, int]], per_step: float,
              capacity: int, reserve: float = 15.0, battery: float = 100.0) -> Preflight:
    if not all(isfinite(float(x)) for x in (per_step, reserve, battery, capacity)) or per_step < 0 or not 0 <= reserve <= 100 or not 0 <= battery <= 100 or capacity < 0:
        raise ValueError('Invalid mission settings')
    issues = []
    if not path or path[0] != farm.rover or path[-1] != farm.rover:
        issues.append('Mission must start and return to the rover base')
    for a, b in zip(path, path[1:]):
        if not farm.in_bounds(*a) or not farm.in_bounds(*b) or farm.cells[b[0]][b[1]] == 'obstacle' or abs(a[0]-b[0])+abs(a[1]-b[1]) != 1:
            issues.append('Route contains an invalid movement or obstacle')
            break
    targets = {(r,c) for r in range(farm.rows) for c in range(farm.cols) if farm.cells[r][c]=='infected'}
    if not targets.issubset(set(path)):
        issues.append('Route does not visit every infected zone')
    if len(targets) > capacity:
        issues.append('Inspection capacity is below the number of infected zones')
    steps = max(0, len(path)-1)
    remaining = round(battery-steps*per_step, 2)
    if remaining < reserve:
        issues.append('Battery reserve would be violated before returning to base')
    return Preflight(not issues, steps, remaining, tuple(issues))
def route_diagnostics(farm: Farm, path: list[tuple[int, int]]) -> dict:
    """Return structured diagnostics for a proposed rover route."""
    invalid_steps = []
    obstacles = []
    infected = []

    for index, (a, b) in enumerate(zip(path, path[1:]), start=1):
        valid = (
            farm.in_bounds(*a)
            and farm.in_bounds(*b)
            and farm.cells[b[0]][b[1]] != 'obstacle'
            and abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
        )
        if not valid:
            invalid_steps.append(index)
        if farm.in_bounds(*b):
            if farm.cells[b[0]][b[1]] == 'obstacle':
                obstacles.append(b)
            if farm.cells[b[0]][b[1]] == 'infected':
                infected.append(b)

    targets = {
        (r, c)
        for r in range(farm.rows)
        for c in range(farm.cols)
        if farm.cells[r][c] == 'infected'
    }

    visited = set(infected)

    return {
        'valid': not invalid_steps,
        'step_count': max(0, len(path) - 1),
        'invalid_steps': invalid_steps,
        'obstacles_encountered': sorted(set(obstacles)),
        'infected_zones_visited': len(visited),
        'infected_zones_total': len(targets),
        'coverage_pct': round(
            len(visited) / len(targets) * 100, 1
        ) if targets else 100.0,
        'starts_at_base': bool(path) and path[0] == farm.rover,
        'returns_to_base': bool(path) and path[-1] == farm.rover,
    }
