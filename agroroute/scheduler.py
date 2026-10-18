"""Backtracking CSP for single-rover nonoverlapping inspection slots."""
from dataclasses import dataclass
@dataclass
class ScheduleResult:
    feasible: bool
    assignments: dict
    nodes: int

def schedule(tasks: list[dict], slots: int=8, use_mrv: bool=True) -> ScheduleResult:
    """Tasks: id, duration (slots), earliest, latest (exclusive end), priority."""
    if len({t['id'] for t in tasks})!=len(tasks): raise ValueError('Task IDs must be unique')
    if slots<1: raise ValueError('slots must be positive')
    domains={}
    for t in tasks:
        duration=int(t['duration']); earliest=int(t.get('earliest',0)); latest=min(slots,int(t.get('latest',slots)))
        if duration<1: raise ValueError('duration must be positive')
        domains[t['id']]=list(range(max(0,earliest),latest-duration+1))
    assigned={}; nodes=0
    def compatible(tid,start):
        duration=next(t['duration'] for t in tasks if t['id']==tid)
        return all(start+duration<=other_start or other_start+next(t['duration'] for t in tasks if t['id']==other_id)<=start for other_id,other_start in assigned.items())
    def solve():
        nonlocal nodes
        if len(assigned)==len(tasks): return True
        remaining=[t for t in tasks if t['id'] not in assigned]
        if use_mrv:
            remaining.sort(key=lambda t:(sum(compatible(t['id'],v) for v in domains[t['id']]),-t.get('priority',0),t['id']))
        t=remaining[0]; tid=t['id']
        for start in domains[tid]:
            nodes+=1
            if compatible(tid,start):
                assigned[tid]=start
                if solve(): return True
                del assigned[tid]
        return False
    ok=solve()
    return ScheduleResult(ok,dict(assigned) if ok else {},nodes)
