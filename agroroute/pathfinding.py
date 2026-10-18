"""Deterministic four-neighbour grid pathfinding, unit-cost edges."""
from __future__ import annotations
from dataclasses import dataclass
import heapq
from itertools import count
from time import perf_counter
from .farm import Farm

Position = tuple[int, int]
ALGORITHMS = ('A*', 'UCS', 'Greedy Best-First')

@dataclass
class SearchResult:
    algorithm: str
    start: Position
    goal: Position
    found: bool
    path: list[Position]
    explored: list[Position]
    cost: int | None
    elapsed_ms: float
    frontier_peak: int

    @property
    def steps(self) -> int:
        return max(0, len(self.path) - 1)

    @property
    def expanded_count(self) -> int:
        return len(self.explored)


def manhattan(a: Position, b: Position) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbours(farm: Farm, node: Position):
    r, c = node
    for nr, nc in ((r-1,c),(r,c+1),(r+1,c),(r,c-1)):
        if farm.in_bounds(nr,nc) and farm.cells[nr][nc] != 'obstacle':
            yield nr, nc


def reconstruct(parent: dict[Position, Position], goal: Position) -> list[Position]:
    path = [goal]
    while path[-1] in parent:
        path.append(parent[path[-1]])
    return path[::-1]


def search(farm: Farm, goal: Position, algorithm: str = 'A*', start: Position | None = None) -> SearchResult:
    if algorithm not in ALGORITHMS:
        raise ValueError(f'Unknown algorithm: {algorithm}')
    start = farm.rover if start is None else start
    for pos, label in ((start,'Start'),(goal,'Destination')):
        if not isinstance(pos, (tuple,list)) or len(pos)!=2 or any(type(x) is not int for x in pos):
            raise ValueError(f'{label} must be a pair of integer coordinates.')
        if not farm.in_bounds(*pos):
            raise ValueError(f'{label} is outside the farm.')
        if farm.cells[pos[0]][pos[1]] == 'obstacle':
            raise ValueError(f'{label} is blocked by an obstacle.')
    start, goal = tuple(start), tuple(goal)
    t0 = perf_counter()
    seq = count()
    def priority(node: Position, g: int) -> int:
        if algorithm == 'UCS': return g
        if algorithm == 'Greedy Best-First': return manhattan(node,goal)
        return g + manhattan(node,goal)
    heap = [(priority(start,0), next(seq), 0, start)]
    best_g = {start: 0}
    parent: dict[Position,Position] = {}
    closed: set[Position] = set()
    explored: list[Position] = []
    peak = 1
    while heap:
        _, _, g, node = heapq.heappop(heap)
        if node in closed or g != best_g[node]:
            continue
        closed.add(node)
        explored.append(node)
        if node == goal:
            path = reconstruct(parent, goal)
            return SearchResult(algorithm,start,goal,True,path,explored,g,(perf_counter()-t0)*1000,peak)
        for nxt in neighbours(farm,node):
            if nxt in closed:
                continue
            new_g = g + 1
            if new_g < best_g.get(nxt,float('inf')):
                best_g[nxt] = new_g
                parent[nxt] = node
                heapq.heappush(heap,(priority(nxt,new_g),next(seq),new_g,nxt))
        peak = max(peak,len(heap))
    return SearchResult(algorithm,start,goal,False,[],explored,None,(perf_counter()-t0)*1000,peak)


def compare(farm: Farm, goal: Position) -> list[SearchResult]:
    return [search(farm,goal,name) for name in ALGORITHMS]
