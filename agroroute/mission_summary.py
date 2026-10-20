"""Helpers for summarizing mission event records."""

def summarize_events(events):
    summary = {"total": 0, "by_event": {}}
    for item in events:
        name = item.get("event")
        if not isinstance(name, str) or not name:
            continue
        summary["total"] += 1
        summary["by_event"][name] = summary["by_event"].get(name, 0) + 1
    return summary
