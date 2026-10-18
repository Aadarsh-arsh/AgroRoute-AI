"""Shared, pure summaries for the unified AgroRoute workflow."""
from .farm import Farm
from .mission import mission
from .mission_control import preflight
from .treatment import build_zone_plans

PLANNERS = ('Nearest Neighbor', 'Genetic Algorithm', 'Exact Dynamic Programming')

def overview(farm: Farm, diagnoses=None, rain=False, confidence_threshold=0.65):
    if not isinstance(farm, Farm):
        raise TypeError('A valid Farm object is required')
    plans = build_zone_plans(farm, diagnoses or {}, rain, confidence_threshold)
    return {
        'name': farm.name,
        'cells': farm.rows * farm.cols,
        'counts': farm.counts(),
        'total_zones': len(plans),
        'high_priority': sum(p.priority == 'High' for p in plans),
        'manual_review': sum(p.manual_review for p in plans),
        'plans': plans,
    }

def prepare_mission(farm: Farm, planner='Genetic Algorithm', battery_per_step=0.4,
                    capacity=20, reserve=15.0):
    if planner not in PLANNERS:
        raise ValueError('Unsupported mission planner')
    result = mission(farm, planner, return_to_base=True)
    check = preflight(farm, result.path if result.found else [], battery_per_step,
                      capacity, reserve) if result.found else None
    return result, check
