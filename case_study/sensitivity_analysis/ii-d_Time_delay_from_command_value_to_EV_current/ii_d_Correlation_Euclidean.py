import sys
import pandas as pd
import numpy as np
import os
import math
from scipy.optimize import linear_sum_assignment

# Set random seed for reproducible simulation [cite: 42]
np.random.seed(42)

cwd = os.getcwd()

# --- (III-B) Charging-current generation model ---
GEN_DIR = f"{cwd}/charging_current_generation"
sys.path.append(GEN_DIR)

from charging_current_generation_model import (
    generate_command_patterns,
    generate_charger_ev_current,
)

# --- (IV) Pair-identification via Correlation-Euclidean ---
# Metric combining correlation coefficient and point-to-point Euclidean distance [cite: 57, 381]
CORR_DIR = f"{cwd}/pair_identification"
sys.path.append(CORR_DIR)

from Correlation_Euclidean import (
    calculate_correlation_euclidean,
    perform_matching_correlation_euclidean
)

# Output directory for II-d sensitivity analysis 
out_dir = os.path.join(
    os.getcwd(),
    "case_study/sensitivity_analysis/ii-d_Time_delay_from_command_value_to_EV_current/accuracy/Correlation_Euclidean"
)

if __name__ == "__main__":
    initial_timestamp = "2024-05-23 15:59:13"
    num_patterns = 300
    command_patterns = generate_command_patterns(num_patterns)

    # Generate simulation data using default model parameters 
    df_charger_generation, df_ev_generation = generate_charger_ev_current(command_patterns, initial_timestamp)
    
    charger_start_time = 0
    charger_interval = 5
    ev_interval = 60

    results_list = []

    # Quantify the effect of time delay II-d on pairing accuracy [cite: 447, 594]
    for ev_start_time in range(0, 30, 1):
        print(f"Time delay (II-d): {ev_start_time}s")
        
        # Subsampling from 1-sec simulation steps [cite: 408]
        df_charger = df_charger_generation[charger_start_time::charger_interval]
        df_ev = df_ev_generation[ev_start_time::ev_interval]

        # Compute evaluation matrix for global and local similarity [cite: 281, 381]
        evaluation_scores = calculate_correlation_euclidean(df_charger, df_ev)
        
        # Globally optimal one-to-one assignment via Hungarian method [cite: 59, 391]
        _, accuracy = perform_matching_correlation_euclidean(evaluation_scores)

        results_list.append({
            "time_delay_II-d": ev_start_time, 
            "pairing_accuracy": accuracy
        })
        
        print(f"Pairing accuracy: {accuracy:.4f}")

    results_df = pd.DataFrame(results_list)
    file_name = f"{num_patterns}p_{ev_interval}s_Cor-Euc_accuracy.csv"
    save_path = os.path.join(out_dir, file_name)
    results_df.to_csv(save_path, index=False)