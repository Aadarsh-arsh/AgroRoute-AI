"""Multi-target route planning using the existing pathfinder."""
from dataclasses import dataclass
from .pathfinding import search

@dataclass(frozen=True)
class InspectionRoute:
    path: tuple
    targets: tuple
    total_steps: int

def plan_inspection_route(farm, targets=None, start=None, algorithm="A*"):
    current = tuple(start if start is not None else farm.rover)
    remaining = list(targets) if targets is not None else [
        (r, c) for r in range(farm.rows) for c in range(farm.cols)
        if farm.cells[r][c] == "infected"
    ]
    if len(set(remaining)) != len(remaining):
        raise ValueError("Targets must not contain duplicates.")
    route, visited = [current], []
    while remaining:
        candidates = []
        for target in remaining:
            result = search(farm, target, algorithm=algorithm, start=current)
            if result.path:
                candidates.append((len(result.path), tuple(target), result.path))
        if not candidates:
            raise ValueError(f"Unreachable inspection targets: {remaining}")
        _, target, segment = min(candidates, key=lambda item: (item[0], item[1]))
        route.extend(tuple(point) for point in segment[1:])
        current = target
        visited.append(target)
        remaining.remove(target)
    return InspectionRoute(tuple(route), tuple(visited), len(route) - 1)
