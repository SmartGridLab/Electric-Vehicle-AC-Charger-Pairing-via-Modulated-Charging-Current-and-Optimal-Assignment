import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[3]
GEN_DIR = ROOT_DIR / "charging_current_generation"
PAIR_DIR = ROOT_DIR / "pair_identification"
sys.path.append(str(GEN_DIR))
sys.path.append(str(PAIR_DIR))

from charging_current_generation_model import (  # noqa: E402
    generate_charger_ev_current,
    generate_command_patterns,
)
from pure_metrics import calculate_pure_euclidean_cost, perform_matching_from_cost  # noqa: E402


if __name__ == "__main__":
    np.random.seed(42)

    out_dir = Path(__file__).resolve().parent / "accuracy"
    out_dir.mkdir(parents=True, exist_ok=True)

    initial_timestamp = "2024-05-23 15:59:13"
    num_patterns_list = [50, 100, 300, 600, 1000]
    charger_start_time = 0
    charger_interval = 5
    ev_interval = 60

    regimes = [(5, "transient"), (25, "steady")]

    for ev_start_time, regime in regimes:
        results_list = []

        for num_patterns in num_patterns_list:
            command_patterns = generate_command_patterns(num_patterns, seed=42)
            df_charger_generation, df_ev_generation = generate_charger_ev_current(
                command_patterns, initial_timestamp, tau=60
            )

            df_charger = df_charger_generation[charger_start_time::charger_interval]
            df_ev = df_ev_generation[ev_start_time::ev_interval]

            cost_matrix = calculate_pure_euclidean_cost(df_charger, df_ev)
            _, accuracy = perform_matching_from_cost(cost_matrix)

            results_list.append(
                {
                    "num_patterns": num_patterns,
                    "Matching_accuracy": accuracy,
                }
            )
            print(f"[Pure Euclidean][Scale][{regime}] pairs={num_patterns}, acc={accuracy:.4f}")

        results_df = pd.DataFrame(results_list)
        file_name = f"Pure-Euc_{regime}_EV_start_time:{ev_start_time}.csv"
        results_df.to_csv(out_dir / file_name, index=False)
        print(f"Saved: {file_name}")
