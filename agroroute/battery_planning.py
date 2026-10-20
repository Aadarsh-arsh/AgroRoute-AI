"""Battery-aware estimates for planned rover routes."""

def estimate_route_energy(path, per_step=1.0, inspection_cost=2.0, targets=0):
    if per_step < 0 or inspection_cost < 0 or targets < 0:
        raise ValueError("Energy costs and target count must be non-negative.")
    steps = max(0, len(path) - 1)
    return steps * per_step + targets * inspection_cost

def is_mission_feasible(path, battery=100.0, reserve=15.0,
                        per_step=1.0, inspection_cost=2.0, targets=0):
    if battery < 0 or reserve < 0 or reserve > battery:
        raise ValueError("Battery and reserve settings are invalid.")
    required = estimate_route_energy(path, per_step, inspection_cost, targets)
    return required <= battery - reserve
