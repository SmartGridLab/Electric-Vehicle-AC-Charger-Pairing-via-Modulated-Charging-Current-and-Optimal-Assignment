import sys
import pandas as pd
import numpy as np
import os

# Ensure consistent command sequence generation across simulations.
np.random.seed(42)

cwd = os.getcwd()

# --- (III-B) Charging-current generation model ---
GEN_DIR = f"{cwd}/charging_current_generation"
sys.path.append(GEN_DIR)

from charging_current_generation_model import (
    generate_command_patterns,
    generate_charger_ev_current,
)

# --- (IV) Pair-identification: Correlation-DTW ---
# Metric robust to timing offsets through elastic time alignment.
CORR_DIR = f"{cwd}/pair_identification"
sys.path.append(CORR_DIR)

from Correlation_DTW import (
    calculate_correlation_dtw,
    perform_matching_correlation_dtw
)

# Set output directory for conservative stress-test bounds.
out_dir = os.path.join(
    os.getcwd(),
    "case_study/scalability_analysis/accuracy"
)

if __name__ == "__main__":
    initial_timestamp = "2024-05-23 15:59:13"
    
    # Evaluate scalability consistent with large-scale coordination studies.
    num_patterns_list = [50, 100, 300, 600, 1000]
    
    # II-d = 25s ensures measurements are taken after current settles.
    charger_start_time = 0
    ev_start_time = 25
    
    charger_interval = 5  
    ev_interval = 60  

    results_list = []

    for num_patterns in num_patterns_list:
        command_patterns = generate_command_patterns(num_patterns)
        
        # Data-driven modeling of charger and EV current sequences.
        df_charger_generation, df_ev_generation = generate_charger_ev_current(
            command_patterns, initial_timestamp
        )
        
        df_charger = df_charger_generation[charger_start_time::charger_interval]
        df_ev = df_ev_generation[ev_start_time::ev_interval]

        # DTW preserves pattern similarity under non-uniform sampling.
        evaluation_scores = calculate_correlation_dtw(df_charger, df_ev)
        
        # Obtain pairing result via the Globally optimal one-to-one assignment.
        _, accuracy = perform_matching_correlation_dtw(evaluation_scores)

        results_list.append({"num_patterns": num_patterns, "pairing_accuracy": accuracy})
        print(f"Number of pairs = {num_patterns} : Pairing accuracy: {accuracy:.4f}")

    results_df = pd.DataFrame(results_list)

    if ev_start_time <= 12:
        file_name = f"Cor-DTW_transient_II-d_{ev_start_time}.csv"
    else:
        file_name = f"Cor-DTW_steady_II-d_{ev_start_time}.csv"

    save_path = os.path.join(out_dir, file_name)
    results_df.to_csv(save_path, index=False)