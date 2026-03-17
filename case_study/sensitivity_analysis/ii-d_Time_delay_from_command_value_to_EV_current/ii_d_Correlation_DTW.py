import sys
import pandas as pd
import numpy as np
import os

# Ensure reproducible generation of command sequences [cite: 406]
np.random.seed(42)

cwd = os.getcwd()

# --- (III-B) Charging-current generation model ---
GEN_DIR = f"{cwd}/charging_current_generation"
sys.path.append(GEN_DIR)

from charging_current_generation_model import (
    generate_command_patterns,
    generate_charger_ev_current,
)

# --- (IV) Pair-identification: Correlation-only baseline ---
# Standard correlation coefficient without distance-based metrics 
CORR_DIR = f"{cwd}/pair_identification"
sys.path.append(CORR_DIR)

from Correlation import (
    calculate_correlation,
    perform_matching_correlation
)

# Output directory for baseline sensitivity study [cite: 610]
out_dir = os.path.join(
    os.getcwd(),
    "case_study/sensitivity_analysis/ii-d_Time_delay_from_command_value_to_EV_current/accuracy"
)

if __name__ == "__main__":
    initial_timestamp = "2024-05-23 15:59:13"
    num_patterns = 300
    command_patterns = generate_command_patterns(num_patterns)

    # Generate waveforms based on experimental verification data [cite: 135]
    df_charger_generation, df_ev_generation = generate_charger_ev_current(
        command_patterns, initial_timestamp, tau=60
    )
    
    charger_start_time = 0
    charger_interval = 5
    ev_interval = 60

    results_list = []

    # Sweep II-d to observe accuracy drops in transient states [cite: 597, 612]
    for ev_start_time in range(0, 30, 1):
        print(f"Time delay (II-d): {ev_start_time}s")
        
        df_charger = df_charger_generation[charger_start_time::charger_interval]
        df_ev = df_ev_generation[ev_start_time::ev_interval]

        # Compute similarity using only the correlation coefficient [cite: 317]
        df_corr = calculate_correlation(df_charger, df_ev)
        
        # Obtain assignment result and evaluate accuracy 
        _, acc = perform_matching_correlation(df_corr)

        results_list.append({
            "time_delay_II-d": ev_start_time, 
            "pairing_accuracy": acc
        })
        
        print(f"Pairing accuracy: {acc:.4f}")

    results_df = pd.DataFrame(results_list)
    file_name = f"{num_patterns}p_{ev_interval}s_Baseline_Cor_accuracy.csv"
    save_path = os.path.join(out_dir, file_name)
    results_df.to_csv(save_path, index=False)