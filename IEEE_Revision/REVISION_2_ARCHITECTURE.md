# Revision (2) Architecture

## Scope

Nomura's clarification changes the target of revision `(2)` as follows.

- Required additional simulations:
  - `I-a` Interval for updating command value
  - `II-d` Time delay from command value to EV current measurement
  - `C` Scalability with the number of EV-charger pairs
- Required added metrics:
  - `Pure DTW`
  - `Pure Euclidean`
- Not required as a new revision target:
  - `Pure Correlation`
    - Reason: correlation-only already exists in the paper as the baseline.
- Not required for this revision package:
  - `II-a / II-b` new pure-metric heatmaps
    - Reason: Nomura explicitly narrowed the new request to `I-a`, `II-d`, and `C`.

This means the final revision package for `(2)` is not "all Table I parameters".
It is a focused comparison package for the three study items above.

## What the paper implies

From the paper and the existing `case_study` scripts:

1. `I-a` is the study corresponding to Section `V-B.1` and Figs. `11` and `12`.
   - It is not a single fixed-delay comparison.
   - The existing implementation computes accuracy over `II-d = 0..29 sec` for each `tau`,
     then the visualization script averages those accuracies by `tau`.
   - Therefore the pure-metric version of `I-a` must follow the same logic.

2. `II-d` is the study corresponding to Section `V-B.3` and Fig. `14`.
   - It explicitly sweeps delay from `0` to `29 sec`.
   - It compares two EV sampling intervals: `30 sec` and `60 sec`.

3. `C. Scalability` is the study corresponding to Section `V-C` and Fig. `15`.
   - Pair counts: `50, 100, 300, 600, 1000`
   - Two operating regimes must be preserved:
     - transient: `II-d = 5 sec`
     - steady: `II-d = 25 sec`

## Design rule

All new scripts must preserve the existing code logic and only remove one metric component.

- `Pure DTW`:
  - start from the existing `Correlation_DTW.py` or `scale_Correlation_DTW.py` flow
  - remove the correlation term
  - keep DTW distance normalization, cost-matrix construction, and Hungarian matching

- `Pure Euclidean`:
  - start from the existing `Correlation_Euclidean.py` or corresponding case-study driver
  - remove the correlation term
  - keep Euclidean distance calculation, normalization, cost-matrix construction, and Hungarian matching

The goal is not improvement or refactoring.
The goal is to observe the result when the composite metric is decomposed into pure components.

## Folder architecture

The final revision tree should follow the same section-based structure as the main repository:

```text
IEEE_Revision/
├── README.md
├── REVISION_2_ARCHITECTURE.md
├── pair_identification/
│   └── pure_metrics.py
└── case_study/
    ├── sensitivity_analysis/
    │   ├── i_a_command_update_interval/
    │   │   ├── accuracy/
    │   │   ├── figures/
    │   │   ├── pure_dtw_i_a.py
    │   │   ├── pure_euclidean_i_a.py
    │   │   └── pure_i_a_accuracy_visualization.py
    │   └── ii-d_Time_delay_from_command_value_to_EV_current/
    │       ├── accuracy/
    │       ├── figures/
    │       ├── pure_dtw_ii_d.py
    │       ├── pure_euclidean_ii_d.py
    │       └── pure_ii_d_accuracy_visualization.py
    └── scalability_analysis/
        ├── accuracy/
        ├── figures/
        ├── pure_dtw_scalability.py
        ├── pure_euclidean_scalability.py
        ├── pure_scale_accuracy_visualization.py
        └── runtime_analysis/
            ├── runtime/
            ├── figures/
            ├── r24_r36_runtime_measurement.py
            └── r24_r36_runtime_visualization.py
```

## Per-folder implementation plan

### 1. `case_study/sensitivity_analysis/i_a_command_update_interval`

Source to mirror:

- `case_study/sensitivity_analysis/i_a_command_update_interval/i_a_Correlation_DTW.py`
- `case_study/sensitivity_analysis/i_a_command_update_interval/i_a_Correlation_Euclidean.py`
- `case_study/sensitivity_analysis/i_a_command_update_interval/i_a_Accuracy_visualization.py`

New simulation scripts:

- `pure_dtw_i_a.py`
- `pure_euclidean_i_a.py`

Fixed/default conditions to preserve:

- number of pairs: `300`
- charger sampling interval (`II-a`): `5 sec`
- EV sampling interval (`II-b`): `30 sec` and `60 sec`
- command update interval (`I-a`): `30, 35, 40, 45, 50, 55, 60 sec`
- delay sweep (`II-d`): `0..29 sec`

Output logic:

- save one CSV per `(EV interval, tau)` combination
- visualization script computes the mean accuracy across `II-d = 0..29`
- generate two final figures:
  - EV interval `30 sec`
  - EV interval `60 sec`

Graph composition:

- existing metrics loaded from `case_study`:
  - `Correlation-DTW`
  - `Correlation-Euclidean`
  - `Baseline (Correlation)`
- new metrics loaded from revision folder:
  - `Pure DTW`
  - `Pure Euclidean`

Result:

- final `I-a` graphs should have five curves, not two or three.

### 2. `case_study/sensitivity_analysis/ii-d_Time_delay_from_command_value_to_EV_current`

Source to mirror:

- `case_study/sensitivity_analysis/ii-d_Time_delay_from_command_value_to_EV_current/ii_d_Correlation.py`
- `case_study/sensitivity_analysis/ii-d_Time_delay_from_command_value_to_EV_current/ii_d_Correlation_Euclidean.py`
- `case_study/sensitivity_analysis/ii-d_Time_delay_from_command_value_to_EV_current/ii_d_Accuracy_visualization.py`

New simulation scripts:

- `pure_dtw_ii_d.py`
- `pure_euclidean_ii_d.py`

Fixed/default conditions to preserve:

- number of pairs: `300`
- command update interval (`I-a`): `60 sec`
- charger sampling interval (`II-a`): `5 sec`
- EV sampling interval (`II-b`): `30 sec` and `60 sec`
- delay sweep (`II-d`): `0..29 sec`

Output logic:

- save separate CSVs for EV interval `30 sec` and `60 sec`
- visualization script should generate:
  - a `30 sec` plot
  - a `60 sec` plot
  - a combined plot

Graph composition:

- existing case-study metrics:
  - `Correlation-DTW`
  - `Correlation-Euclidean`
  - `Baseline (Correlation)`
- revision-only new metrics:
  - `Pure DTW`
  - `Pure Euclidean`

### 3. `case_study/scalability_analysis`

Source to mirror:

- `case_study/scalability_analysis/scale_Correlation_DTW.py`
- `case_study/scalability_analysis/scale_Correlation_Euclidean.py`
- `case_study/scalability_analysis/scale_Correlation.py`
- `case_study/scalability_analysis/scale_Accuracy_visualization.py`

New simulation scripts:

- `pure_dtw_scalability.py`
- `pure_euclidean_scalability.py`

Fixed/default conditions to preserve:

- pair counts: `50, 100, 300, 600, 1000`
- charger sampling interval (`II-a`): `5 sec`
- EV sampling interval (`II-b`): `60 sec`
- command update interval (`I-a`): `60 sec`
- transient regime: `II-d = 5 sec`
- steady regime: `II-d = 25 sec`

Output logic:

- save transient and steady CSVs separately for each pure metric
- visualization script generates one combined figure aligned with Fig. `15`

Graph composition:

- existing case-study metrics:
  - `Correlation-DTW`
  - `Correlation-Euclidean`
  - `Baseline (Correlation)`
- revision-only new metrics:
  - `Pure DTW`
  - `Pure Euclidean`

## Naming convention

For clarity, each revision folder should keep the same output style:

- `accuracy/`: raw CSV outputs
- `figures/`: final plot outputs
- simulation drivers:
  - `pure_dtw_<study>.py`
  - `pure_euclidean_<study>.py`
- visualization:
  - `pure_<study>_accuracy_visualization.py`
- shared pure-metric utilities:
  - `pair_identification/pure_metrics.py`

This keeps the revision package aligned with the original repository structure while remaining separate from the published `case_study` tree.

## Existing `(2) pure_graph` folder

The existing exploratory folder reference:

- `IEEE_Revision/case_study/...`

should be treated as an exploratory prototype, not the final architecture.

Reason:

- it focuses on `Pure Correlation` and `Pure DTW`
- it does not match the narrowed scope from Nomura
- the final revision package now needs `Pure DTW` + `Pure Euclidean` across `I-a`, `II-d`, and `Scalability`

## Final interpretation

So the correct revision-2 work package is:

- do not expand to every Table I item
- do not add new `II-a / II-b` pure-metric heatmaps
- do add `Pure DTW` and `Pure Euclidean` to:
  - `I-a`
  - `II-d`
  - `C. Scalability`
- keep the original code logic and only remove the complementary metric term
- generate graphs that can be directly compared against the existing Section V figures
