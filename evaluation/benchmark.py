"""Reproducible AgroRoute benchmarks. Run: python -m evaluation.benchmark"""
from __future__ import annotations
import csv
import json
import platform
import statistics
from pathlib import Path
from time import perf_counter
from agroroute.farm import Farm, demo_farm
from agroroute.pathfinding import ALGORITHMS, search
from agroroute.mission import mission, infected_zones
from agroroute.deep_learning import image_manifest, split_manifest

OUT=Path(__file__).resolve().parent/"results"
REPEATS=7
ROUTE_ALGORITHMS=("Nearest Neighbor","Genetic Algorithm","Exact Dynamic Programming")

def scenarios():
    demo=demo_farm()
    plain=Farm(rows=12,cols=12,name="Open field")
    for r,c in [(2,2),(2,9),(8,9),(10,4)]: plain.paint(r,c,"infected")
    maze=Farm(rows=12,cols=12,name="Barrier field")
    for r in range(11):
        if r!=6: maze.paint(r,5,"obstacle")
    for r,c in [(1,3),(3,9),(8,8),(10,2)]: maze.paint(r,c,"infected")
    return {"demo":demo,"open":plain,"barrier":maze}

def write_csv(path,rows):
    if not rows:return
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    path_rows=[]; route_rows=[]; raw_path=[]; raw_route=[]
    for name,farm in scenarios().items():
        goals=infected_zones(farm)
        for goal in goals:
            optimal=search(farm,goal,"UCS")
            for alg in ALGORITHMS:
                trials=[search(farm,goal,alg) for _ in range(REPEATS)]
                r=trials[0]
                times=[v.elapsed_ms for v in trials]
                raw_path.extend(dict(scenario=name,goal_row=goal[0]+1,goal_col=goal[1]+1,
                                     algorithm=alg,trial=i+1,elapsed_ms=round(t,6))
                                for i,t in enumerate(times))
                path_rows.append(dict(scenario=name,goal_row=goal[0]+1,goal_col=goal[1]+1,
                                      algorithm=alg,found=r.found,path_steps=r.steps if r.found else "",
                                      optimal_steps=optimal.steps if optimal.found else "",
                                      optimality_gap_steps=r.steps-optimal.steps if r.found and optimal.found else "",
                                      expanded_nodes=r.expanded_count,frontier_peak=r.frontier_peak,
                                      median_ms=round(statistics.median(times),5),
                                      min_ms=round(min(times),5),max_ms=round(max(times),5)))
        baseline=mission(farm,"Exact Dynamic Programming")
        for alg in ROUTE_ALGORITHMS:
            trials=[mission(farm,alg) for _ in range(REPEATS)]
            r=trials[0]
            times=[v.elapsed_ms for v in trials]
            raw_route.extend(dict(scenario=name,algorithm=alg,trial=i+1,
                                  elapsed_ms=round(t,6)) for i,t in enumerate(times))
            route_rows.append(dict(scenario=name,algorithm=alg,zones=len(goals),
                                   found=r.found,round_trip_steps=r.cost if r.found else "",
                                   exact_optimal_steps=baseline.cost if baseline.found else "",
                                   gap_steps=r.cost-baseline.cost if r.found and baseline.found else "",
                                   gap_pct=round(100*(r.cost-baseline.cost)/baseline.cost,2)
                                     if r.found and baseline.found and baseline.cost else "",
                                   evaluations=r.evaluations,median_ms=round(statistics.median(times),5),
                                   min_ms=round(min(times),5),max_ms=round(max(times),5),
                                   returned_to_base=bool(r.found and r.path[-1]==farm.rover),
                                   all_zones_visited=bool(r.found and set(goals).issubset(r.path))))
    for filename,rows in [("pathfinding_summary.csv",path_rows),("route_optimization_summary.csv",route_rows),
                          ("pathfinding_raw_timings.csv",raw_path),("route_raw_timings.csv",raw_route)]:
        write_csv(OUT/filename,rows)
    model=Path("models/mobile_net_v2/metadata.json")
    model_file=Path("models/mobile_net_v2/model.keras")
    dataset=Path("data/plant_leaves")
    model_status={"metadata_present":model.is_file(),"model_file_present":model_file.is_file(),
                  "dataset_present":dataset.is_dir(),
                  "verification":"not possible without original metadata/model and held-out dataset"}
    if model.is_file():
        try:
            data=json.loads(model.read_text(encoding="utf-8"))
            model_status["saved_metrics"]={k:data.get(k) for k in
                 ("classes","split_counts","mobilenet","decision_tree","seed","epochs_run")}
            model_status["verification"]="metadata read; independent test-set re-evaluation not performed"
        except (ValueError,OSError) as e:
            model_status["metadata_error"]=str(e)
    if dataset.is_dir():
        try:
            rows=image_manifest(dataset)
            model_status["dataset_image_count"]=len(rows)
            model_status["dataset_classes"]=sorted(set(label for _,label in rows))
            model_status["expected_split_counts"]={k:len(v) for k,v in split_manifest(rows).items()}
        except (ValueError,ImportError) as e:
            model_status["dataset_error"]=str(e)
    (OUT/"model_verification.json").write_text(json.dumps(model_status,indent=2),encoding="utf-8")
    manifest={"repeats":REPEATS,"farm_scenarios":list(scenarios()),"pathfinding_cases":len(path_rows),
              "route_cases":len(route_rows),"timer":"time.perf_counter internal algorithm elapsed_ms",
              "environment":{"python":platform.python_version(),"platform":platform.platform()},
              "caveats":["Academic synthetic farm scenarios, not field trials",
                         "Time is environment dependent and excludes UI rendering",
                         "Exact DP is only used on four-zone scenarios",
                         "GA seed=42; timings vary but outputs deterministic",
                         "Model accuracy not independently verified without saved files and test data"]}
    (OUT/"benchmark_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    assert all(r["optimality_gap_steps"]==0 for r in path_rows if r["algorithm"] in ("A*","UCS"))
    assert all(r["gap_steps"]>=0 and r["returned_to_base"] and r["all_zones_visited"] for r in route_rows)
    print(json.dumps({"pathfinding_cases":len(path_rows),"route_cases":len(route_rows),
                      "model_status":model_status["verification"]},indent=2))
    return path_rows,route_rows,model_status

if __name__=="__main__":
    run()
