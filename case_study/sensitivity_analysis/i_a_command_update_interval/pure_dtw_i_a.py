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
from pure_metrics import calculate_pure_dtw_cost, perform_matching_from_cost  # noqa: E402


if __name__ == "__main__":
    np.random.seed(42)

    out_dir = Path(__file__).resolve().parent / "accuracy"
    out_dir.mkdir(parents=True, exist_ok=True)

    initial_timestamp = "2024-05-23 15:59:13"
    num_patterns = 300
    command_patterns = generate_command_patterns(num_patterns, seed=42)

    charger_interval = 5
    ev_intervals = [30, 60]
    taus = [60, 55, 50, 45, 40, 35, 30]

    for ev_interval in ev_intervals:
        for tau in taus:
            df_charger_generation, df_ev_generation = generate_charger_ev_current(
                command_patterns, initial_timestamp, tau=tau
            )

            results = []
            for offset in range(30):
                print(f"[Pure DTW][I-a] EV={ev_interval}s, tau={tau}s, delay={offset}s")

                df_charger = df_charger_generation.iloc[0::charger_interval]
                df_ev = df_ev_generation.iloc[offset::ev_interval]

                cost_matrix = calculate_pure_dtw_cost(df_charger, df_ev)
                _, acc = perform_matching_from_cost(cost_matrix)

                results.append(
                    {
                        "time_delay_command_to_ev_measurement_s": offset,
                        "pairing_accuracy": acc,
                    }
                )

            df_result = pd.DataFrame(results)
            fname = f"{num_patterns}p_evint{ev_interval}_tau{tau}_PureDTWAcc.csv"
            df_result.to_csv(out_dir / fname, index=False)
            print(f"Saved: {fname}")
