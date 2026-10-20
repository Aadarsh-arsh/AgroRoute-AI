"""Structured event logging for rover missions."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

@dataclass(frozen=True)
class MissionEvent:
    event: str
    timestamp: str
    details: dict[str, Any]

class MissionEventLog:
    def __init__(self):
        self._events: list[MissionEvent] = []

    def record(self, event: str, **details: Any) -> MissionEvent:
        if not event or not event.strip():
            raise ValueError("Event name must not be empty.")
        item = MissionEvent(event.strip(), datetime.now(timezone.utc).isoformat(), dict(details))
        self._events.append(item)
        return item

    @property
    def events(self):
        return tuple(self._events)

    def to_list(self):
        return [asdict(item) for item in self._events]

    def count(self, event: str) -> int:
        return sum(item.event == event for item in self._events)

    def clear(self):
        self._events.clear()
