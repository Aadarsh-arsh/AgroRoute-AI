"""Safe, testable orchestration of the one-click crop-inspection workflow."""
from __future__ import annotations
from dataclasses import dataclass
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
from typing import Any
from .farm import Farm
from .dashboard import prepare_mission, overview
from .rover import RoverState

@dataclass
class WorkflowResult:
    farm: Farm
    diagnoses: dict[str, Any]
    predicted_label: str | None
    probability: float | None
    zone: tuple[int, int] | None
    overview: dict
    route: Any
    preflight: Any
    fingerprint: str
    battery_per_step: float
    capacity: int
    reserve: float
    @property
    def ready(self) -> bool:
        return bool(self.route.found and self.preflight and self.preflight.feasible)

def image_fingerprint(data: bytes) -> str:
    return sha256(data).hexdigest()

def validate_image(data: bytes, max_bytes: int = 12 * 1024 * 1024) -> None:
    if not data or len(data) > max_bytes:
        raise ValueError("Upload a leaf image smaller than 12 MB.")
    from PIL import Image, UnidentifiedImageError
    try:
        with Image.open(BytesIO(data)) as im:
            if im.format not in ("JPEG", "PNG", "WEBP"):
                raise ValueError("Only JPG, PNG and WEBP are supported.")
            if im.width * im.height > 25_000_000:
                raise ValueError("Image dimensions are too large.")
            im.verify()
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError("The uploaded file is not a valid image.") from exc

def build_workflow(farm: Farm, diagnoses: dict | None = None, *,
                   image_bytes: bytes | None = None, zone: tuple[int,int] | None = None,
                   severity: str = "Medium", model_dir="models/mobile_net_v2",
                   predictor=None, planner="Genetic Algorithm", battery_per_step=0.4,
                   capacity=20, reserve=15.0, rain=False, confidence_threshold=0.65) -> WorkflowResult:
    """Plan without mutating the user's farm. A low-confidence result still requires review.

    An image requires a selected zone; existing marked zones can be planned without an image.
    Predictor injection allows deterministic tests without TensorFlow.
    """
    working = Farm.from_dict(deepcopy(farm.to_dict()))
    updated = dict(diagnoses or {})
    label = None
    probability = None
    if image_bytes is not None:
        validate_image(image_bytes)
        if zone is None or not working.in_bounds(*zone):
            raise ValueError("Select a valid farm zone for the uploaded image.")
        if zone == working.rover or working.cells[zone[0]][zone[1]] == "obstacle":
            raise ValueError("Choose a zone that is neither the rover base nor an obstacle.")
        if severity not in ("Low", "Medium", "High"):
            raise ValueError("Invalid severity.")
        if predictor is None:
            from .deep_learning import predict_image
            predictor = predict_image
        label, probability, _ = predictor(model_dir, image_bytes)
        probability = float(probability)
        if not 0 <= probability <= 1:
            raise ValueError("Model returned an invalid probability.")
        # Healthy predictions must not silently erase an existing infected zone.
        if label.strip().lower() != "healthy":
            working.paint(*zone, "infected", severity)
            updated[working.key(*zone)] = {
                "class": label, "probability": probability,
                "severity": severity, "model": "MobileNetV2"
            }
    details = overview(working, updated, rain, confidence_threshold)
    route, check = prepare_mission(working, planner, battery_per_step, capacity, reserve)
    return WorkflowResult(working, updated, label, probability, zone, details, route, check,
                          image_fingerprint(image_bytes) if image_bytes is not None else "",
                          float(battery_per_step), int(capacity), float(reserve))

def start_rover(result: WorkflowResult, capacity: int) -> RoverState:
    if not result.ready:
        raise ValueError("Mission failed preflight and cannot be started.")
    if capacity != result.capacity:
        raise ValueError("Inspection capacity changed after mission preflight.")
    return RoverState(list(result.route.path), capacity=capacity)

def simulate_to_completion(result: WorkflowResult, battery_per_step: float,
                           capacity: int) -> RoverState:
    if battery_per_step != result.battery_per_step:
        raise ValueError("Battery consumption changed after mission preflight.")
    rover = start_rover(result, capacity)
    while rover.status not in ("Completed", "Blocked", "Battery depleted", "Invalid route",
                               "Inspection capacity reached", "No route"):
        if not rover.tick(result.farm, battery_per_step):
            break
    return rover

def workflow_report(result: WorkflowResult, rover: RoverState | None = None) -> dict:
    report = {
        "farm": result.farm.name,
        "model_prediction": result.predicted_label,
        "model_probability_uncalibrated": result.probability,
        "image_sha256": result.fingerprint or None,
        "selected_zone": [result.zone[0]+1, result.zone[1]+1] if result.zone else None,
        "planner": result.route.algorithm,
        "route_found": result.route.found,
        "preflight_passed": result.ready,
        "battery_consumption_per_step_pct": result.battery_per_step,
        "required_reserve_pct": result.reserve,
        "inspection_capacity": result.capacity,
        "preflight_issues": list(result.preflight.issues) if result.preflight else [result.route.message],
        "route_steps": len(result.route.path)-1 if result.route.found else None,
        "route": [[r+1,c+1] for r,c in result.route.path],
        "zone_plans": [plan.to_dict() for plan in result.overview["plans"]],
        "note": "Academic simulation. Disease probability is uncalibrated; treatment requires human verification."
    }
    if rover is not None:
        report["rover"] = {"status": rover.status, "steps_completed": rover.step,
                           "battery_remaining_pct": rover.battery,
                           "inspected_zones": [[r+1,c+1] for r,c in rover.inspected]}
    return report
