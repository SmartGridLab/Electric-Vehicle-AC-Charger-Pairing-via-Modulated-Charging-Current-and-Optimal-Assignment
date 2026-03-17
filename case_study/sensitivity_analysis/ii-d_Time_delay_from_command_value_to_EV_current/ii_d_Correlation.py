import sys
import pandas as pd
import numpy as np
import os

# Ensure reproducibility of command-pattern generation [cite: 42, 406]
np.random.seed(42)

cwd = os.getcwd()

# --- (III-B) Charging-current generation model ---
GEN_DIR = f"{cwd}/charging_current_generation"
sys.path.append(GEN_DIR)

from charging_current_generation_model import (
    generate_command_patterns,
    generate_charger_ev_current,
)

# --- (IV) Pair-identification via Correlation-DTW ---
# DTW elastically warps the time axis to align waveforms [cite: 335, 658]
CORR_DIR = f"{cwd}/pair_identification"
sys.path.append(CORR_DIR)

from Correlation_DTW import (
    calculate_correlation_dtw,
    perform_matching_correlation_dtw
)

# Output directory for sensitivity analysis of parameter II-d 
out_dir = os.path.join(
    os.getcwd(),
    "case_study/sensitivity_analysis/ii-d_Time_delay_from_command_value_to_EV_current/accuracy/CorrelationDTW"
)

if __name__ == "__main__":
    # Initial timestamp for the data-exchange phase [cite: 72]
    initial_timestamp = "2024-05-23 15:59:13"
    
    # Generate unique command patterns for 300 EV-charger pairs [cite: 406, 448]
    num_patterns = 300
    command_patterns = generate_command_patterns(num_patterns)
    
    # Stage I & II: Generate charger and EV current sequences (τ = 60s) [cite: 140, 420]
    df_charger_generation, df_ev_generation = generate_charger_ev_current(command_patterns, initial_timestamp)
    
    # Define sampling intervals for charger (II-a) and EV (II-b) 
    charger_start_time = 0
    charger_interval = 5  # Charger-side sampling interval: 5s
    ev_interval = 60      # EV-side sampling interval: 60s

    results_list = []

    # Sweep time delay II-d from 0 to 29 seconds to evaluate sensitivity [cite: 594]
    for ev_start_time in range(0, 30, 1):
        print(f"Time delay (II-d): {ev_start_time}s")
        
        # Subsample sequences based on defined intervals and timing offsets [cite: 408]
        df_charger_sample = df_charger_generation[charger_start_time::charger_interval]
        df_ev_sample = df_ev_generation[ev_start_time::ev_interval]

        # Compute cost matrix using Correlation-DTW composite metric [cite: 381, 537]
        cost_matrix = calculate_correlation_dtw(df_charger_sample, df_ev_sample)
        
        # Perform optimal assignment using the Hungarian method [cite: 390, 592]
        _, accuracy = perform_matching_correlation_dtw(cost_matrix)

        results_list.append({
            "time_delay_II-d": ev_start_time,
            "pairing_accuracy": accuracy
        })

        print(f"Pairing accuracy: {accuracy:.4f}")

    # Export sensitivity analysis results to CSV 
    results_df = pd.DataFrame(results_list)
    file_name = f"{num_patterns}p_{ev_interval}s_Cor-DTW_accuracy.csv"
    save_path = os.path.join(out_dir, file_name)
    results_df.to_csv(save_path, index=False)