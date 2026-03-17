import os
import re
from pathlib import Path
from typing import Dict, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

# -------- Paths --------
CWD       = os.getcwd()
# Define relative paths based on the MCCT framework structure [cite: 63, 404]
BASE_DIR  = Path(CWD) / "case_study" / "sensitivity_analysis" / "ii_ab_Charger_and_EV_sampling_interval"
ACC_DIR_DTW = BASE_DIR / "accuracy" / "Correlation-DTW"
ACC_DIR_EUC = BASE_DIR / "accuracy" / "Correlation-Euclidean"
PLOT_DIR  = BASE_DIR / "figures"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

# Updated output filenames as requested
OUT_DTW = PLOT_DIR / "heatmap_Correlation-DTW.png"
OUT_EUC = PLOT_DIR / "heatmap_Correlation-Euclidean.png"

# -------- Grid definition (Sensitivity Analysis) --------
# Charger-side (II-a) and EV-side (II-b) sampling intervals 
CHARGER_INTERVALS = [5, 10, 30, 60]  # Rows (II-a)
EV_INTERVALS      = [5, 10, 30, 60]  # Columns (II-b)

# -------- Discrete thresholds & color palette --------
# Define thresholds for the heatmap based on pairing accuracy levels [cite: 478, 482]
T1, T2, T3, T4, T5 = 50.0, 60.0, 70.0, 80.0, 90.0
COLORS = ["#f2b8b5", "#f3c7a8", "#f5dca9", "#e7efb0", "#c4e3c5", "#9bcda6"]
CMAP   = ListedColormap(COLORS)
BOUNDS = [0.0, T1, T2, T3, T4, T5, 100.0001]
NORM   = BoundaryNorm(BOUNDS, len(COLORS))

# -------- Filename parsing --------
# Pattern to extract sampling intervals from filenames (e.g., "...Chint5_EVint30...") [cite: 420]
TAIL_RE = re.compile(r"Chint(\d+)_EVint(\d+)", re.IGNORECASE)

def parse_pair(name: str) -> Optional[Tuple[int, int]]:
    """Extract (charger_interval, ev_interval) from the simulation result filename."""
    m = TAIL_RE.search(name)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))

def csv_mean_accuracy(csv_path: Path) -> Optional[float]:
    """Calculate the average pairing accuracy (%) from the evaluation results."""
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        return None

    cand = [c for c in df.columns if "acc" in c.lower()]
    if cand:
        s = pd.to_numeric(df[cand[0]], errors="coerce")
        val = float(np.nanmean(s.values))
    else:
        num = df.select_dtypes(include=[np.number])
        if num.size == 0:
            return None
        val = float(np.nanmean(num.values))

    if np.isnan(val):
        return None
    # Normalize to percentage if values are ratios (0..1)
    if 0.0 <= val <= 1.0:
        val *= 100.0
    return val

def collect_means_from_dir(target_dir: Path) -> Dict[Tuple[int,int], float]:
    """Scan the directory and aggregate pairing accuracy for each sampling interval combo."""
    results: Dict[Tuple[int,int], float] = {}
    if not target_dir.exists():
        print(f"Warning: Directory not found: {target_dir}")
        return results

    for p in target_dir.glob("*.csv"):
        pair = parse_pair(p.name)
        if pair is None:
            continue
        val = csv_mean_accuracy(p)
        if val is not None:
            # Maintain the latest available calculation for each pair
            results[pair] = val
    return results

def grid_matrix(means: Dict[Tuple[int,int], float]) -> np.ndarray:
    """Construct a matrix corresponding to the sweep of II-a and II-b intervals[cite: 592]."""
    M = np.full((len(CHARGER_INTERVALS), len(EV_INTERVALS)), np.nan, dtype=float)
    for i, charger in enumerate(CHARGER_INTERVALS):
        for j, ev in enumerate(EV_INTERVALS):
            val = means.get((charger, ev))
            if val is not None:
                M[i, j] = val
    return M

def plot_grid(M: np.ndarray, title: str, out_path: Path):
    """Render a heatmap illustrating the effect of sampling intervals on average pairing accuracy[cite: 592]."""
    fig, ax = plt.subplots(figsize=(9, 6))
    data = np.ma.masked_invalid(M)
    im = ax.imshow(data, aspect="equal", cmap=CMAP, norm=NORM)
    
    # Large timestamp differences can make metrics undefined ("Null") [cite: 568-569]
    im.cmap.set_bad(color="#d9d9d9")

    # Configure axes with labels matching the paper's figures [cite: 592]
    ax.set_xticks(range(len(EV_INTERVALS)))
    ax.set_yticks(range(len(CHARGER_INTERVALS)))
    ax.set_xticklabels([f"EV {v}s" for v in EV_INTERVALS], fontsize=20)
    ax.set_yticklabels([f"Charger {v}s" for v in CHARGER_INTERVALS], fontsize=20)
    ax.set_title(title, fontsize=24, pad=10)

    # Grid line configuration for visual clarity
    ax.set_xticks(np.arange(-0.5, len(EV_INTERVALS), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(CHARGER_INTERVALS), 1), minor=True)
    ax.grid(which="minor", linewidth=0.6, color="#bbbbbb")
    ax.tick_params(which="minor", bottom=False, left=False)

    # Annotate cells with pairing accuracy percentages
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            text = "Null" if np.isnan(v) else f"{v:.1f}%"
            ax.text(j, i, text, ha="center", va="center", fontsize=20, color="#222222")

    # Add discrete colorbar for pairing accuracy levels
    fig.colorbar(im, ax=ax, boundaries=BOUNDS, ticks=BOUNDS).ax.tick_params(labelsize=15)
    
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    print(f"Saved: {out_path}")
    plt.show()

def main():
    # Collect results independently for each composite similarity metric 
    dtw_means = collect_means_from_dir(ACC_DIR_DTW)
    euc_means = collect_means_from_dir(ACC_DIR_EUC)

    # Generate matrices for heatmap rendering
    M_dtw = grid_matrix(dtw_means)
    M_euc = grid_matrix(euc_means)

    # Plot results for both Correlation–DTW and Correlation–Euclidean
    plot_grid(M_dtw, "Correlation–DTW", OUT_DTW)
    plot_grid(M_euc, "Correlation–Euclidean", OUT_EUC)

if __name__ == "__main__":
    main()