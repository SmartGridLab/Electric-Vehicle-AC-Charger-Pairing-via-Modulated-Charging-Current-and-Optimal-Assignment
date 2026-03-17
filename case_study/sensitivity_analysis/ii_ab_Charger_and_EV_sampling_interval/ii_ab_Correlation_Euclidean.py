import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# ===== Reproducibility =====
# Set random seed to ensure reproducibility of command-pattern generation
np.random.seed(42)

# ===== Path Configuration =====
cwd = Path(os.getcwd())

# --- (III-B) Charging-current generation model ---
GEN_DIR = f"{cwd}/charging_current_generation"
sys.path.append(GEN_DIR)

from charging_current_generation_model import (
    generate_command_patterns,
    generate_charger_ev_current,
)

# --- (IV) Pair-identification: Correlation-Euclidean ---
# This metric combines the correlation coefficient with Euclidean distance
CORR_DIR = f"{cwd}/pair_identification"
sys.path.append(CORR_DIR)

from Correlation_Euclidean import (
    calculate_correlation_euclidean,
    perform_matching_correlation_euclidean
)

# ===== Output Directory Settings =====
# Target directory for Correlation-Euclidean sensitivity analysis
BASE = cwd / "case_study" / "sensitivity_analysis" / "ii_ab_Charger_and_EV_sampling_interval"
ACC_DIR = BASE / "accuracy" / "Correlation-Euclidean"
ACC_DIR.mkdir(parents=True, exist_ok=True)

# Candidate sampling intervals (II-a, II-b)
INTERVALS = [5, 10, 30, 60]


def run_one_combo(
    ev_interval: int,
    charger_interval: int,
    command_patterns,
    initial_timestamp: str,
    tau: int,
    offset_max: int = 30,
):
    """
    Execute pairing simulation for a specific sampling interval combination.
    Calculates Pairing accuracy using the Correlation-Euclidean composite metric.
    """
    num_p = len(command_patterns)
    fname = f"{num_p}p_Chint{charger_interval}_EVint{ev_interval}_Correlation-Euclidean_Acc.csv"
    out_path = ACC_DIR / fname

    if out_path.exists():
        print(f"[SKIP existing] EV={ev_interval}, CH={charger_interval} -> {out_path.name}")
        return

    print(f"[RUN] Correlation-Euclidean: EV={ev_interval}s, CH={charger_interval}s")

    try:
        # Generate charger and EV current waveforms (1-sec simulation step)
        df_charger_generation, df_ev_generation = generate_charger_ev_current(
            command_patterns, initial_timestamp, tau=tau
        )

        results = []

        # Sweep the time delay from command value to EV current measurement (II-d)
        for offset in range(offset_max):
            print(
                f"  [EV={ev_interval}s, CH={charger_interval}s, tau={tau}s, delay={offset}s] Computing..."
            )

            # Subsample sequences to specified sampling intervals
            df_charger = df_charger_generation.iloc[0::charger_interval]
            df_ev = df_ev_generation.iloc[offset::ev_interval]

            # Compute similarity matrix and perform optimal assignment via Hungarian method
            df_score = calculate_correlation_euclidean(df_charger, df_ev)
            _, acc = perform_matching_correlation_euclidean(df_score)

            print(f"    -> Pairing accuracy: {acc:.4f}")
            results.append(
                {
                    "time_delay_command_to_ev_measurement_s": offset,
                    "pairing_accuracy": acc,
                }
            )

        # Save results to CSV
        df_result = pd.DataFrame(results)
        df_result.to_csv(out_path, index=False)
        print(f"  └ saved: {out_path.name}")

    except Exception as e:
        print(f"[ERROR] EV={ev_interval}, CH={charger_interval} -> {type(e).__name__}: {e}")


def main():
    # Simulation parameters from Section V-A
    initial_timestamp = "2024-05-23 15:59:13"
    num_patterns = 300  
    tau = 60            # Command update period (I-a)
    offset_max = 30     # Max sweep range for time delay (II-d)

    # Generate unique command patterns for MCCT
    command_patterns = generate_command_patterns(num_patterns)

    for ev_interval in INTERVALS:
        for charger_interval in INTERVALS:
            run_one_combo(
                ev_interval,
                charger_interval,
                command_patterns,
                initial_timestamp,
                tau,
                offset_max=offset_max,
            )


if __name__ == "__main__":
    main()