import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import os
from pathlib import Path
from matplotlib.ticker import MultipleLocator

# -------- Paths Configuration --------
# Define relative paths for the sensitivity analysis of parameter II-d[cite: 593, 420].
BASE_DIR = Path("case_study/sensitivity_analysis/ii-d_Time_delay_from_command_value_to_EV_current")
ACC_DIR  = BASE_DIR / "accuracy"
output_dir = BASE_DIR / "figures"
output_dir.mkdir(parents=True, exist_ok=True)

# -------- Data Loading --------
def load_acc_data(interval, metric):
    """Helper function to load CSV results based on the EV-side sampling interval (II-b) and metric[cite: 420, 595]."""
    return pd.read_csv(ACC_DIR / f"300_{interval}interval_{metric}_accuracy.csv")

# Load accuracy datasets for 30s and 60s EV sampling intervals across proposed metrics and baseline[cite: 595, 610].
df_30_coreuc = load_acc_data(30, "Cor-Euc")
df_30_cor    = load_acc_data(30, "Cor")
df_30_cordtw = load_acc_data(30, "Cor-DTW")

df_60_coreuc = load_acc_data(60, "Cor-Euc")
df_60_cor    = load_acc_data(60, "Cor")
df_60_cordtw = load_acc_data(60, "Cor-DTW")

# -------- Visualization Settings --------
# Axis labels aligned with the terminology in Section V-B.3 and Fig. 14[cite: 594, 611, 612].
xlabel = 'Time delay from command value to EV current measurement [sec]'
ylabel = 'Accuracy [%]'
yticks = [10 * i for i in range(11)]

def plot_accuracy(df_coreuc, df_cordtw, df_cor, fname):
    """Plot pairing accuracy for a single sampling interval scenario[cite: 410, 612]."""
    fig, ax = plt.subplots(figsize=(11, 7))

    # Convert pairing accuracy to percentage for visualization[cite: 410, 602].
    ax.plot(df_coreuc['command_ev_samplingTime_diff'],
            df_coreuc['Matching_accuracy'] * 100,
            marker='s', linewidth=2, color='#228b22', label='Correlation-Euclidean')
    ax.plot(df_cordtw['command_ev_samplingTime_diff'],
            df_cordtw['Matching_accuracy'] * 100,
            marker='o', linewidth=2, color='#ff8c00', label='Correlation-DTW')
    ax.plot(df_cor['command_ev_samplingTime_diff'],
            df_cor['Matching_accuracy'] * 100,
            marker='^', linestyle='dashed', color='#376ea4', linewidth=2, label='Baseline (Correlation)')

    # Labels and axis formatting matching paper implementation guidelines[cite: 61, 612].
    ax.set_xlabel(xlabel, fontsize=23, labelpad=10)
    ax.set_ylabel(ylabel, fontsize=26, labelpad=0)

    # X-axis scale settings for time delay II-d[cite: 611].
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.tick_params(axis='x', which='major', labelsize=20, length=5)
    ax.tick_params(axis='x', which='minor', labelsize=0,  length=5)
    
    # Y-axis scale settings for pairing accuracy[cite: 602].
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(10))
    ax.tick_params(axis='y', which='major', labelsize=20, length=5)
    ax.tick_params(axis='y', which='minor', labelsize=0,  length=5)
    
    # Grid configuration for clarity.
    ax.grid(which='major', linestyle='-', linewidth=0.8, alpha=1)
    ax.grid(which='minor', linestyle='-', linewidth=0.8, alpha=1)

    # Limits and Legend.
    ax.set_xlim(0, 29)
    ax.set_ylim(0, 102)
    ax.legend(loc='lower right', fontsize=20)

    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, fname))
    plt.close(fig)

def plot_accuracy_combined(d30_coreuc, d30_cordtw, d30_cor,
                           d60_coreuc, d60_cordtw, d60_cor,
                           fname):
    """Render combined plot comparing multiple metrics and sampling intervals as in Fig. 14[cite: 612, 610]."""
    fig, ax = plt.subplots(figsize=(11, 7))

    # Map metrics to specific visual styles[cite: 610].
    methods = [
        ("Correlation-Euclidean", 's', '#228b22', d30_coreuc, d60_coreuc),
        ("Correlation-DTW",       'o', '#ff8c00', d30_cordtw, d60_cordtw),
        ("Baseline (Correlation)",'^', '#376ea4', d30_cor,    d60_cor),
    ]

    # Plot 30s interval results using solid lines[cite: 610].
    for label, marker, color, df30, df60 in methods:
        ax.plot(df30['command_ev_samplingTime_diff'],
                df30['Matching_accuracy'] * 100,
                marker=marker, linewidth=2, linestyle='-',
                color=color, label=f'{label} (EV interval: 30s)')

    # Plot 60s interval results using dashed lines[cite: 610].
    for label, marker, color, df30, df60 in methods:
        ax.plot(df60['command_ev_samplingTime_diff'],
                df60['Matching_accuracy'] * 100,
                marker=marker, linewidth=2, linestyle='--',
                color=color, label=f'{label} (EV interval: 60s)')

    ax.set_xlabel(xlabel, fontsize=23, labelpad=10)
    ax.set_ylabel(ylabel, fontsize=26, labelpad=0)

    # Synchronize ticks and grid with individual plots.
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(10))
    ax.tick_params(axis='x', which='major', labelsize=20, length=5)
    ax.tick_params(axis='x', which='minor', labelsize=0,  length=5)
    ax.tick_params(axis='y', which='major', labelsize=20, length=5)
    ax.tick_params(axis='y', which='minor', labelsize=0,  length=5)

    ax.grid(which='major', linestyle='-', linewidth=0.8, alpha=1)
    ax.grid(which='minor', linestyle='-', linewidth=0.8, alpha=1)

    ax.set_xlim(0, 29)
    ax.set_ylim(0, 102)
    ax.legend(loc='lower right', fontsize=18, ncol=1)

    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, fname))
    plt.close(fig)

# Generate plots for 30s, 60s, and combined sensitivity scenarios[cite: 595, 612].
plot_accuracy(df_30_coreuc, df_30_cordtw, df_30_cor, "ii_d_accuracy_ev_interval:30s.png")
plot_accuracy(df_60_coreuc, df_60_cordtw, df_60_cor, "ii_d_accuracy_ev_interval:60s.png")
plot_accuracy_combined(df_30_coreuc, df_30_cordtw, df_30_cor,
                       df_60_coreuc, df_60_cordtw, df_60_cor,
                       "ii_d_accuracy_all.png")