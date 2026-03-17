import sys
import pandas as pd
import numpy as np
import os

# Ensure reproducibility of command-pattern generation.
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
# Standard correlation coefficient capturing overall waveform similarity.
CORR_DIR = f"{cwd}/pair_identification"
sys.path.append(CORR_DIR)

from Correlation import (
    calculate_correlation,
    perform_matching_correlation
)

# Set output directory for scalability analysis.
out_dir = os.path.join(
    os.getcwd(),
    "case_study/scalability_analysis/accuracy"
)

if __name__ == "__main__":
    # Common initial timestamp for the data-exchange phase.
    initial_timestamp = "2024-05-23 15:59:13"
    
    # Vary the number of simultaneously connected EV-charger pairs.
    num_patterns_list = [50, 100, 300, 600, 1000]
    
    # Timing parameters: II-a (Charger) and II-d (EV time delay).
    # Set II-d to 25s for steady state or 5s for transient state.
    charger_start_time = 0
    ev_start_time = 25
    
    # Sampling intervals for charger (II-a) and EV (II-b).
    charger_interval = 5  
    ev_interval = 60  

    results_list = []

    for num_patterns in num_patterns_list:
        # Generate unique command patterns assigned to each charger.
        command_patterns = generate_command_patterns(num_patterns)
        
        # Generate charger and EV current waveforms based on experimental data.
        df_charger_generation, df_ev_generation = generate_charger_ev_current(
            command_patterns, initial_timestamp
        )
        
        # Subsample sequences to reflect non-uniform sampling and timing offsets.
        df_charger = df_charger_generation[charger_start_time::charger_interval]
        df_ev = df_ev_generation[ev_start_time::ev_interval]

        # Compute similarity matrix using the correlation coefficient.
        df_correlations = calculate_correlation(df_charger, df_ev)
        
        # Globally optimal one-to-one assignment via the Hungarian method.
        _, accuracy = perform_matching_correlation(df_correlations)

        # Store pairing accuracy for the given scale.
        results_list.append({"num_patterns": num_patterns, "pairing_accuracy": accuracy})
        print(f"Number of pairs = {num_patterns} : Pairing accuracy: {accuracy:.4f}")

    results_df = pd.DataFrame(results_list)
    
    # Classify file names based on operating regimes (Transient or Steady state).
    if ev_start_time <= 12:
        file_name = f"Cor_transient_II-d_{ev_start_time}.csv"
    else:
        file_name = f"Cor_steady_II-d_{ev_start_time}.csv"

    save_path = os.path.join(out_dir, file_name)
    results_df.to_csv(save_path, index=False)