"""Conservative decision support for simulated crop inspection (not pesticide prescriptions)."""
from dataclasses import dataclass, asdict
from .farm import Farm
from .expert import forward_chain

@dataclass
class ZonePlan:
    row: int
    column: int
    severity: str
    disease: str
    probability: float | None
    priority: str
    action: str
    reason: str
    manual_review: bool
    spraying_allowed: bool

    def to_dict(self):
        return asdict(self)


def _diagnosis(raw):
    if isinstance(raw, str):
        return raw, None
    if isinstance(raw, dict):
        disease = raw.get('disease') or raw.get('predicted_class') or raw.get('class') or 'Unknown'
        probability = raw.get('probability', raw.get('confidence'))
        if probability is not None:
            try:
                probability = float(probability)
                if probability > 1 and probability <= 100:
                    probability /= 100
                if not 0 <= probability <= 1:
                    probability = None
            except (TypeError, ValueError):
                probability = None
        return str(disease), probability
    return 'Unknown', None


def build_zone_plans(farm: Farm, diagnoses: dict | None = None, rain: bool = False,
                     confidence_threshold: float = 0.65) -> list[ZonePlan]:
    if not 0 <= confidence_threshold <= 1:
        raise ValueError('Confidence threshold must be between 0 and 1')
    diagnoses = diagnoses or {}
    plans = []
    for r in range(farm.rows):
        for c in range(farm.cols):
            if farm.cells[r][c] != 'infected':
                continue
            key = farm.key(r,c)
            disease, probability = _diagnosis(diagnoses.get(key))
            severity = farm.severities.get(key, 'Medium')
            rules = forward_chain(disease, severity, rain=rain)
            manual = probability is None or probability < confidence_threshold or disease == 'Unknown'
            if manual:
                action = 'Inspect and verify disease before choosing any treatment'
                reason = 'Unverified or low-confidence image classification'
            elif disease.lower() == 'healthy':
                action = 'Recheck marked zone and monitor crop'
                reason = 'Image prediction is healthy despite infected zone marking'
            else:
                action = 'Inspect symptoms; consult local agronomist and approved product label'
                reason = 'Suspected disease requires confirmation before treatment'
            if rain:
                action += '; postpone spraying during rain'
            priority = 'High' if severity == 'High' else 'Medium' if severity == 'Medium' else 'Low'
            plans.append(ZonePlan(r+1,c+1,severity,disease,probability,priority,action,reason,manual,not rain))
    priority_order = {'High':0,'Medium':1,'Low':2}
    return sorted(plans,key=lambda p:(priority_order[p.priority],p.row,p.column))


def mission_feasibility(steps: int, battery: float, consumption_per_step: float,
                        reserve_pct: float = 15.0, zones: int = 0, capacity: int = 20) -> dict:
    if steps < 0 or zones < 0 or capacity < 0 or not 0 <= battery <= 100 or consumption_per_step < 0 or not 0 <= reserve_pct <= 100:
        raise ValueError('Invalid mission feasibility parameters')
    needed = steps * consumption_per_step
    remaining = battery - needed
    issues = []
    if remaining < reserve_pct:
        issues.append('Insufficient battery to complete mission with required reserve')
    if zones > capacity:
        issues.append('Inspection capacity smaller than infected-zone count')
    return {'feasible':not issues,'estimated_consumption_pct':round(needed,2),
            'estimated_remaining_pct':round(remaining,2),'issues':issues,
            'note':'Battery estimates are illustrative; not calibrated to physical hardware.'}
