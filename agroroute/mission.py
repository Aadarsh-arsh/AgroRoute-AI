"""Multi-zone rover missions: obstacle-aware pairwise paths, exact DP, greedy, GA."""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from itertools import permutations
from random import Random
from time import perf_counter
from .farm import Farm
from .pathfinding import search, Position

@dataclass
class MissionResult:
    algorithm: str
    found: bool
    order: list[Position]
    path: list[Position]
    cost: int | None
    elapsed_ms: float
    evaluations: int
    message: str = ''


def infected_zones(farm: Farm) -> list[Position]:
    return [(r,c) for r in range(farm.rows) for c in range(farm.cols) if farm.cells[r][c]=='infected']


def distance_matrix(farm: Farm, zones: list[Position]):
    """Use UCS for every unordered pair; cache both directions."""
    points = [farm.rover] + zones
    paths = {}
    for i in range(len(points)):
        paths[i,i] = [points[i]]
        for j in range(i+1,len(points)):
            result = search(farm,points[j],algorithm='UCS',start=points[i])
            paths[i,j] = result.path if result.found else None
            paths[j,i] = list(reversed(result.path)) if result.found else None
    return points, paths


def mission(farm: Farm, algorithm='Genetic Algorithm', return_to_base=True,
            population=80, generations=180, seed=42, max_exact_zones=11) -> MissionResult:
    """Find a visit order; all leg costs are true obstacle-aware UCS distances.

    Exact DP is the optimal benchmark; GA is stochastic with reproducible seed.
    """
    if algorithm not in ('Genetic Algorithm','Nearest Neighbor','Exact Dynamic Programming'):
        raise ValueError('Unknown mission algorithm')
    t0=perf_counter()
    zones=infected_zones(farm)
    n=len(zones)
    if n==0:
        return MissionResult(algorithm,False,[],[],None,(perf_counter()-t0)*1000,0,'Add at least one infected zone.')
    if algorithm=='Exact Dynamic Programming' and n>max_exact_zones:
        return MissionResult(algorithm,False,[],[],None,(perf_counter()-t0)*1000,0,f'Exact solver limited to {max_exact_zones} zones.')
    if n>20:
        return MissionResult(algorithm,False,[],[],None,(perf_counter()-t0)*1000,0,'Limit the mission to 20 infected zones for interactive performance.')
    points,paths=distance_matrix(farm,zones)
    if any(paths[0,i] is None for i in range(1,n+1)):
        return MissionResult(algorithm,False,[],[],None,(perf_counter()-t0)*1000,0,'At least one infected zone is unreachable from the rover.')
    def dist(i,j): return len(paths[i,j])-1
    def score(order):
        seq=[0]+list(order)+([0] if return_to_base else [])
        return sum(dist(a,b) for a,b in zip(seq,seq[1:]))
    evaluations=0
    if algorithm=='Nearest Neighbor':
        left=set(range(1,n+1)); order=[]; current=0
        while left:
            nxt=min(left,key=lambda i:(dist(current,i),i))
            order.append(nxt);left.remove(nxt);current=nxt
        evaluations=n
    elif algorithm=='Exact Dynamic Programming':
        @lru_cache(None)
        def dp(current, mask):
            if mask==(1<<n)-1:
                return (dist(current,0) if return_to_base else 0,())
            options=[]
            for i in range(1,n+1):
                if not mask & (1<<(i-1)):
                    remainder,tail=dp(i,mask | (1<<(i-1)))
                    options.append((dist(current,i)+remainder,(i,)+tail))
            return min(options,key=lambda item:(item[0],item[1]))
        _,chosen=dp(0,0)
        order=list(chosen)
        evaluations=dp.cache_info().misses
    else:
        if population<4 or generations<1:
            raise ValueError('Population must be >= 4 and generations >= 1.')
        rng=Random(seed)
        base=list(range(1,n+1))
        pool=[tuple(rng.sample(base,n)) for _ in range(population)]
        pool[0]=tuple(sorted(base,key=lambda i:dist(0,i)))
        def tournament():
            return min(rng.sample(pool,min(4,len(pool))),key=score)
        def crossover(a,b):
            if n<2:return a
            left,right=sorted(rng.sample(range(n+1),2))
            child=[None]*n
            child[left:right]=a[left:right]
            remain=[v for v in b if v not in child]
            it=iter(remain)
            return tuple(v if v is not None else next(it) for v in child)
        best=min(pool,key=score)
        for _ in range(generations):
            pool.sort(key=score)
            if score(pool[0])<score(best):best=pool[0]
            next_pool=pool[:2]
            while len(next_pool)<population:
                child=list(crossover(tournament(),tournament()))
                if n>1 and rng.random()<.22:
                    i,j=rng.sample(range(n),2)
                    child[i],child[j]=child[j],child[i]
                next_pool.append(tuple(child))
            pool=next_pool
        candidate=min(pool,key=score)
        order=list(min((best,candidate),key=score))
        evaluations=population*(generations+1)
    indices=[0]+order+([0] if return_to_base else [])
    full=[]
    for a,b in zip(indices,indices[1:]):
        segment=paths[a,b]
        full.extend(segment if not full else segment[1:])
    return MissionResult(algorithm,True,[points[i] for i in indices],full,score(order),
                         (perf_counter()-t0)*1000,evaluations)
