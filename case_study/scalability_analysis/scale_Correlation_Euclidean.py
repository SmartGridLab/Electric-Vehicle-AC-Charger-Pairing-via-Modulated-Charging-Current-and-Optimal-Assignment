import sys
import pandas as pd
import numpy as np
import os

# Ensure reproducible simulation results.
np.random.seed(42)

cwd = os.getcwd()

# --- (III-B) Charging-current generation model ---
GEN_DIR = f"{cwd}/charging_current_generation"
sys.path.append(GEN_DIR)

from charging_current_generation_model import (
    generate_command_patterns,
    generate_charger_ev_current,
)

# --- (IV) Pair-identification: Correlation-Euclidean ---
# Composite metric combining global correlation and local Euclidean distance.
CORR_DIR = f"{cwd}/pair_identification"
sys.path.append(CORR_DIR)

from Correlation_Euclidean import (
    calculate_correlation_euclidean,
    perform_matching_correlation_euclidean
)

# Set output directory for scalability case study.
out_dir = os.path.join(
    os.getcwd(),
    "case_study/scalability_analysis/accuracy"
)

if __name__ == "__main__":
    initial_timestamp = "2024-05-23 15:59:13"
    
    # Scale from 50 to 1,000 EV-charger pairs.
    num_patterns_list = [50, 100, 300, 600, 1000]
    
    # Timing configuration: Steady state guaranteed if II-d is extended.
    charger_start_time = 0
    ev_start_time = 25
    
    charger_interval = 5  
    ev_interval = 60  

    results_list = []

    for num_patterns in num_patterns_list:
        command_patterns = generate_command_patterns(num_patterns)
        
        # Stage I & II: Waveform generation per Algorithm 1.
        df_charger_generation, df_ev_generation = generate_charger_ev_current(
            command_patterns, initial_timestamp
        )
        
        df_charger = df_charger_generation[charger_start_time::charger_interval]
        df_ev = df_ev_generation[ev_start_time::ev_interval]

        # Compute evaluation matrix using the Hadamard product.
        evaluation_scores = calculate_correlation_euclidean(df_charger, df_ev)
        
        # Optimal assignment to minimize total cost in the cost matrix.
        _, accuracy = perform_matching_correlation_euclidean(evaluation_scores)

        results_list.append({"num_patterns": num_patterns, "pairing_accuracy": accuracy})
        print(f"Number of pairs = {num_patterns} : Pairing accuracy: {accuracy:.4f}")

    results_df = pd.DataFrame(results_list)

    if ev_start_time <= 12:
        file_name = f"Cor-Euc_transient_II-d_{ev_start_time}.csv"
    else:
        file_name = f"Cor-Euc_steady_II-d_{ev_start_time}.csv"

    save_path = os.path.join(out_dir, file_name)
    results_df.to_csv(save_path, index=False)