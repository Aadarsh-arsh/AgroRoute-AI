import json
from pathlib import Path

from .farm import Farm


def save_scenario(farm: Farm, path: str | Path) -> None:
    """Save a farm scenario as readable UTF-8 JSON."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(
        farm.to_dict(),
        indent=2,
        ensure_ascii=False,
    )
    destination.write_text(content + "\n", encoding="utf-8")


def load_scenario(path: str | Path) -> Farm:
    """Load and validate a farm scenario from a JSON file."""
    source = Path(path)

    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid scenario JSON: {exc.msg}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError("Invalid farm scenario: expected a JSON object.")

    try:
        return Farm.from_dict(data)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid farm scenario: {exc}") from exc
