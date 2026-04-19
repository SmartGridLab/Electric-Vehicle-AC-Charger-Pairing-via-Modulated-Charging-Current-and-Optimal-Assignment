import argparse
import os
import sys
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[4]
GEN_DIR = ROOT_DIR / "charging_current_generation"
PAIR_DIR = ROOT_DIR / "pair_identification"
REV_PAIR_DIR = Path(__file__).resolve().parents[3] / "pair_identification"
# In restricted environments, disable multiprocessing for joblib-based functions.
os.environ.setdefault("JOBLIB_MULTIPROCESSING", "0")
sys.path.append(str(GEN_DIR))
sys.path.append(str(PAIR_DIR))
sys.path.append(str(REV_PAIR_DIR))

from charging_current_generation_model import (  # noqa: E402
    generate_charger_ev_current,
    generate_command_patterns,
)
from Correlation import calculate_correlation, perform_matching_correlation  # noqa: E402
from Correlation_DTW import calculate_correlation_dtw, perform_matching_correlation_dtw  # noqa: E402
from Correlation_Euclidean import (  # noqa: E402
    calculate_correlation_euclidean,
    perform_matching_correlation_euclidean,
)
from pure_metrics import (  # noqa: E402
    calculate_pure_dtw_cost,
    calculate_pure_euclidean_cost,
    perform_matching_from_cost,
)


METHODS = {
    "Correlation": (calculate_correlation, perform_matching_correlation),
    "Correlation+DTW": (calculate_correlation_dtw, perform_matching_correlation_dtw),
    "Correlation+Euclidean": (
        calculate_correlation_euclidean,
        perform_matching_correlation_euclidean,
    ),
    "Pure-DTW": (calculate_pure_dtw_cost, perform_matching_from_cost),
    "Pure-Euclidean": (calculate_pure_euclidean_cost, perform_matching_from_cost),
}


def parse_pair_list(text: str) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def parse_method_list(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="R2-4 + R3-6 runtime measurement for scalability (up to 1000x1000 pairs)."
    )
    parser.add_argument("--pair-list", default="50,100,300,600,1000")
    parser.add_argument(
        "--methods",
        default="Correlation,Correlation+DTW,Correlation+Euclidean,Pure-DTW,Pure-Euclidean",
        help=(
            "Comma-separated list from: Correlation, Correlation+DTW, "
            "Correlation+Euclidean, Pure-DTW, Pure-Euclidean"
        ),
    )
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--tau", type=int, default=60)
    parser.add_argument("--charger-start-time", type=int, default=0)
    parser.add_argument("--charger-interval", type=int, default=5)
    parser.add_argument("--ev-start-time", type=int, default=25)
    parser.add_argument("--ev-interval", type=int, default=60)
    return parser


def main() -> None:
    args = build_parser().parse_args()

    pair_list = parse_pair_list(args.pair_list)
    method_list = parse_method_list(args.methods)
    for method in method_list:
        if method not in METHODS:
            raise ValueError(f"Unknown method: {method}")

    out_dir = Path(__file__).resolve().parent / "runtime"
    out_dir.mkdir(parents=True, exist_ok=True)

    initial_timestamp = "2024-05-23 15:59:13"
    rows: list[dict] = []

    for repeat_idx in range(args.repeats):
        run_seed = args.seed + repeat_idx
        np.random.seed(run_seed)

        for num_patterns in pair_list:
            command_patterns = generate_command_patterns(num_patterns=num_patterns, seed=run_seed)
            df_charger_generation, df_ev_generation = generate_charger_ev_current(
                command_patterns, initial_timestamp, tau=args.tau
            )

            df_charger = df_charger_generation[args.charger_start_time::args.charger_interval]
            df_ev = df_ev_generation[args.ev_start_time::args.ev_interval]

            for method in method_list:
                calc_fn, match_fn = METHODS[method]

                t0 = perf_counter()
                score_or_cost = calc_fn(df_charger, df_ev)
                t1 = perf_counter()
                _, accuracy = match_fn(score_or_cost)
                t2 = perf_counter()

                cost_matrix_sec = t1 - t0
                assignment_sec = t2 - t1
                total_sec = t2 - t0

                rows.append(
                    {
                        "method": method,
                        "num_patterns": num_patterns,
                        "repeat": repeat_idx + 1,
                        "ev_start_time": args.ev_start_time,
                        "cost_matrix_sec": cost_matrix_sec,
                        "assignment_sec": assignment_sec,
                        "total_sec": total_sec,
                        "matching_accuracy": accuracy,
                    }
                )
                print(
                    f"[runtime] repeat={repeat_idx + 1}, pairs={num_patterns}, method={method}, "
                    f"cost={cost_matrix_sec:.3f}s, assign={assignment_sec:.3f}s, total={total_sec:.3f}s"
                )

    raw_df = pd.DataFrame(rows)
    summary_df = (
        raw_df.groupby(["method", "num_patterns"], as_index=False)
        .agg(
            cost_matrix_sec_mean=("cost_matrix_sec", "mean"),
            cost_matrix_sec_std=("cost_matrix_sec", "std"),
            assignment_sec_mean=("assignment_sec", "mean"),
            assignment_sec_std=("assignment_sec", "std"),
            total_sec_mean=("total_sec", "mean"),
            total_sec_std=("total_sec", "std"),
            matching_accuracy_mean=("matching_accuracy", "mean"),
        )
        .sort_values(["method", "num_patterns"])
    )

    raw_path = out_dir / "r24_r36_runtime_raw.csv"
    summary_path = out_dir / "r24_r36_runtime_summary.csv"
    raw_df.to_csv(raw_path, index=False)
    summary_df.to_csv(summary_path, index=False)

    print(f"Saved raw runtime CSV: {raw_path}")
    print(f"Saved summary runtime CSV: {summary_path}")


if __name__ == "__main__":
    main()
