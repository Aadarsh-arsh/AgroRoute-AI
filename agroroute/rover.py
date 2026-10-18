"""Deterministic, tick-based virtual rover execution."""
from dataclasses import dataclass, field
from .farm import Farm

@dataclass
class RoverState:
    path: list[tuple[int,int]]
    step: int = 0
    battery: float = 100.0
    capacity: int = 20
    inspected: list[tuple[int,int]] = field(default_factory=list)
    status: str = 'Ready'

    @property
    def position(self):
        return self.path[self.step] if self.path else None

    def tick(self, farm: Farm, battery_per_step: float = 0.4):
        if not 0 <= battery_per_step <= 100:
            raise ValueError('Invalid battery consumption rate')
        if self.status in ('Completed', 'Blocked', 'Battery depleted', 'Invalid route', 'Inspection capacity reached', 'No route'):
            return False
        if not self.path:
            self.status='No route'; return False
        if self.step >= len(self.path)-1:
            self.status='Completed'; return False
        if self.battery < battery_per_step:
            self.status='Battery depleted'; return False
        nxt=self.path[self.step+1]
        if not farm.in_bounds(*nxt) or farm.cells[nxt[0]][nxt[1]]=='obstacle':
            self.status='Blocked'; return False
        if abs(nxt[0]-self.position[0])+abs(nxt[1]-self.position[1])!=1:
            self.status='Invalid route'; return False
        if farm.cells[nxt[0]][nxt[1]]=='infected' and nxt not in self.inspected and self.capacity <= 0:
            self.status='Inspection capacity reached'; return False
        self.step+=1
        self.battery=round(max(0,self.battery-battery_per_step),3)
        if farm.cells[nxt[0]][nxt[1]]=='infected' and nxt not in self.inspected:
            self.inspected.append(nxt)
            self.capacity-=1
        self.status='Completed' if self.step==len(self.path)-1 else 'Moving'
        return True
