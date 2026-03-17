import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import os
from pathlib import Path
from matplotlib.ticker import MultipleLocator

# -------- Paths Configuration --------
# Set relative paths for the scalability analysis of multiple EV–charger pairs.
BASE_DIR   = Path("case_study/scalability_analysis")
ACC_DIR    = BASE_DIR / "accuracy"
output_dir = BASE_DIR / "figures"
output_dir.mkdir(parents=True, exist_ok=True)

# -------- Data Loading --------
def load_scalability_data(algo, regime, time):
    """
    Load simulation results for transient or steady state operating regimes based on specific metrics and time delays.
    """
    filename = f"{algo}_{regime}_EV_start_time:{time}.csv"
    return pd.read_csv(ACC_DIR / filename)

# Load datasets for transient (delay II-d = 5 sec) and steady state (delay II-d = 25 sec) regimes.
df_5_coreuc  = load_scalability_data("Cor-Euc", "transient", 5)
df_5_cor     = load_scalability_data("Cor",     "transient", 5)
df_5_cordtw  = load_scalability_data("Cor-DTW", "transient", 5)

df_25_coreuc = load_scalability_data("Cor-Euc", "steady", 25)
df_25_cor    = load_scalability_data("Cor",     "steady", 25)
df_25_cordtw = load_scalability_data("Cor-DTW", "steady", 25)

# -------- Visualization Settings --------
# Use axis labels and terminology consistent with Section V-C of the research paper.
xlabel = 'Number of EV–charger pairs'
ylabel = 'Accuracy [%]'
yticks = [10 * i for i in range(11)]

def plot_accuracy(df_coreuc, df_cordtw, df_cor, df_25_coreuc, df_25_dtw, df_25_cor, fname, loc='center right'):
    """
    Render a comparison of pairing accuracy across different scales for transient and steady state regimes.
    """
    fig, ax = plt.subplots(figsize=(11, 7))

    # Plot results for the transient state using dashed lines for proposed and baseline metrics.
    ax.plot(df_coreuc['num_patterns'],
            df_coreuc['Matching_accuracy'] * 100,
            marker='s', linestyle='dashed', linewidth=2, color='#228b22', label='Correlation-Euclidean (transient)')
    ax.plot(df_cordtw['num_patterns'],
            df_cordtw['Matching_accuracy'] * 100,
            marker='o', linestyle='dashed', linewidth=2, color='#ff8c00', label='Correlation-DTW (transient)')
    ax.plot(df_cor['num_patterns'],
            df_cor['Matching_accuracy'] * 100,
            marker='^', linestyle='dashed', linewidth=2, color='#376ea4', label='Baseline (transient)')
    
    # Plot results for the steady state using solid lines where pairing accuracy is typically higher.
    ax.plot(df_25_coreuc['num_patterns'],
            df_25_coreuc['Matching_accuracy'] * 100,
            marker='s', linewidth=2, color='#228b22', label='Correlation-Euclidean (steady)')
    ax.plot(df_25_dtw['num_patterns'],
            df_25_dtw['Matching_accuracy'] * 100,
            marker='o', linewidth=2, color='#ff8c00', label='Correlation-DTW (steady)')
    ax.plot(df_25_cor['num_patterns'],
            df_25_cor['Matching_accuracy'] * 100,
            marker='^', linewidth=2, color='#376ea4', label='Baseline (steady)')

    # Configure axis labels and formatting for pairing accuracy and pair count.
    ax.set_xlabel(xlabel, fontsize=30, labelpad=10)
    ax.set_ylabel(ylabel, fontsize=30)
    
    # Set x-ticks based on the predefined number of simultaneously connected EV–charger pairs.
    xticks = df_coreuc['num_patterns']
    ax.set_xticks(xticks)
    ax.tick_params(axis='x', which='major', labelsize=20, length=5)
    
    # Set y-axis for pairing accuracy percentage with major grid lines.
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.tick_params(axis='y', which='major', labelsize=20, length=5)
    ax.grid(which='major', linestyle='-', linewidth=0.8, alpha=1)

    # Configure plot limits and legend placement.
    ax.set_ylim(0, 102)
    ax.legend(loc=loc, fontsize=22)    

    plt.tight_layout()
    fig.savefig(output_dir / fname)
    plt.close(fig)

# Generate the scalability comparison plot corresponding to Fig. 15 in the study.
plot_accuracy(df_5_coreuc, df_5_cordtw, df_5_cor, df_25_coreuc, df_25_cordtw, df_25_cor, "scale_accuracy_all.png")