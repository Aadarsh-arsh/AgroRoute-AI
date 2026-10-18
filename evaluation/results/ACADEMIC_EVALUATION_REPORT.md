# AgroRoute AI — Experimental Evaluation Report

## Scope and reproducibility
Results were generated from the audited project's original algorithm implementations using `python -m evaluation.benchmark`. Three deterministic synthetic 12×12 farm scenarios were used: demo, open and barrier. Each contains four infected zones. Each search or mission was executed seven times; elapsed time is the median of algorithm-reported `perf_counter` measurements in milliseconds. Results are machine-dependent and do not measure Streamlit rendering or real-world robot performance. GA uses the existing default seed 42, population 80 and 180 generations. All routes return to the rover base.

## Pathfinding: A*, UCS, Greedy Best-First
Twelve start-to-zone tasks per algorithm (four zones × three farms):

| Algorithm | Mean expanded nodes | Mean median time (ms) | Nonoptimal paths (of 12) |
|---|---:|---:|---:|
| A* | 42.33 | 0.0753 | 0 |
| UCS | 72.00 | 0.1137 | 0 |
| Greedy Best-First | 13.33 | 0.0267 | 0 |

A* and UCS were optimal for every tested target. Greedy also happened to find optimal paths in these 12 cases; this **does not** establish that Greedy is optimal in general. Search effort and timing differences are scenario-dependent. The full per-goal measurements are in `pathfinding_summary.csv`.

## Multi-zone route optimization
All routes use UCS-computed obstacle-aware pairwise distances. Exact DP is the reference optimum for these four-zone problems.

| Scenario | Nearest Neighbor | Genetic Algorithm | Exact DP | NN gap |
|---|---:|---:|---:|---:|
| demo | 38 | 38 | 38 | 0.0% |
| open | 38 | 38 | 38 | 0.0% |
| barrier | 48 | 46 | 46 | 4.35% |

On the barrier scenario, Nearest Neighbor required 48 steps, versus 46 for GA and Exact DP (4.35% longer). On demo and open, all three achieved the same route length. GA performed substantially more objective evaluations and took longer in this small-scale test; exact DP should not be generalized to large numbers of zones due to exponential scaling. All nine tested mission plans covered all zones and returned to base.

## Disease-classifier metrics: verification status
**Not independently verified in this evaluation environment.** The distributed project does not contain `models/mobile_net_v2/model.keras`, `models/mobile_net_v2/metadata.json`, or the original `data/plant_leaves` images. Prior conversation reported MobileNetV2 test accuracy **83%** and Decision Tree **72%**, using a shared split of 240 train / 60 validation / 100 test images. These are **previously reported values, not newly verified results**; do not present them as independently reproduced measurements. The training source uses a seeded stratified 60% / 15% / 25% split, but matching saved metadata and held-out predictions are required to verify confusion matrices, precision, recall and F1. No new model training or inference was performed.

On the user's Windows machine, with the original model and dataset restored, run `python -m evaluation.benchmark` to regenerate benchmarks and inspect `evaluation/results/model_verification.json`. The metadata fields `mobilenet` and `decision_tree` include per-class metrics and confusion matrices from the saved training run; **reading metadata alone is not independent verification**. For independent re-evaluation, run a dedicated inference pass on the original held-out images and compare the resulting confusion matrices. Retraining produces a new experiment and should be labeled separately.

## Limitations
- Synthetic grids; no agricultural field trial, physical rover, spraying validation or clinical-grade disease diagnosis.
- Three hand-selected scenarios and only four infected zones per scenario; performance conclusions are limited.
- Timing on a shared virtual machine is sensitive to background load and Python overhead; repeat on the presentation laptop for comparable timing.
- Greedy's optimality in these cases is coincidental, not guaranteed.
- Model metrics are unverified until original artifacts are available.

## Files
- `pathfinding_summary.csv` — per target, path length, optimality, expanded nodes, peak frontier, median timing.
- `route_optimization_summary.csv` — per scenario, route length, exact gap, evaluations, timing and coverage.
- `pathfinding_raw_timings.csv`, `route_raw_timings.csv` — seven raw timing observations each.
- `pathfinding_expanded_nodes.png`, `route_quality.png` — report-ready figures.
- `model_verification.json`, `benchmark_manifest.json` — evidence and reproducibility status.
