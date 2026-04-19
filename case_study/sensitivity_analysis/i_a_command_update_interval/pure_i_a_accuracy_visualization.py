import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[3]
CASE_BASE = ROOT_DIR / "case_study/sensitivity_analysis/i_a_command_update_interval/accuracy"
PURE_BASE = Path(__file__).resolve().parent / "accuracy"
OUT_DIR = Path(__file__).resolve().parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TAU_LIST = [30, 35, 40, 45, 50, 55, 60]
EV_INTERVALS = [30, 60]
NUM_PATTERNS = 300

METHODS = ["CorEuc", "CorrDTW", "Corr", "PureEuc", "PureDTW"]
LABELS = {
    "CorEuc": "Correlation-Euclidean",
    "CorrDTW": "Correlation-DTW",
    "Corr": "Baseline (Correlation)",
    "PureEuc": "Pure Euclidean",
    "PureDTW": "Pure DTW",
}
COLORS = {
    "CorEuc": "#228b22",
    "CorrDTW": "#ff8c00",
    "Corr": "#376ea4",
    "PureEuc": "#a23ecf",
    "PureDTW": "#d84b5b",
}
MARKERS = {"CorEuc": "s", "CorrDTW": "o", "Corr": "^", "PureEuc": "D", "PureDTW": "x"}
LINESTYLES = {"CorEuc": "-", "CorrDTW": "-", "Corr": "dashed", "PureEuc": "-", "PureDTW": "-"}


def _load_mean_accuracy(path: Path) -> float:
    if not path.exists():
        return np.nan
    df = pd.read_csv(path)
    if "pairing_accuracy" in df.columns:
        return float(df["pairing_accuracy"].mean() * 100.0)
    if "accuracy" in df.columns:
        return float(df["accuracy"].mean() * 100.0)
    return float(df["Matching_accuracy"].mean() * 100.0)


def _path_for(method: str, ev_int: int, tau: int) -> Path:
    if method == "Corr":
        return CASE_BASE / "Correlation" / f"{NUM_PATTERNS}p_evint{ev_int}_tau{tau}_CorrAcc.csv"
    if method == "CorrDTW":
        return CASE_BASE / "Correlation_DTW" / f"{NUM_PATTERNS}p_evint{ev_int}_tau{tau}_CorrDTWAcc.csv"
    if method == "CorEuc":
        return CASE_BASE / "Correlation_Euclidean" / f"{NUM_PATTERNS}_{ev_int}sInterval_CorEuc_tau{tau}s_accuracy.csv"
    if method == "PureEuc":
        return PURE_BASE / f"{NUM_PATTERNS}p_evint{ev_int}_tau{tau}_PureEucAcc.csv"
    return PURE_BASE / f"{NUM_PATTERNS}p_evint{ev_int}_tau{tau}_PureDTWAcc.csv"


def load_all(ev_int: int) -> dict[str, list[float]]:
    avg_pct = {m: [] for m in METHODS}
    for tau in TAU_LIST:
        for method in METHODS:
            avg_pct[method].append(_load_mean_accuracy(_path_for(method, ev_int, tau)))
    return avg_pct


def plot_line(avg_pct: dict[str, list[float]], ev_int: int) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_axisbelow(True)

    for method in METHODS:
        ax.plot(
            TAU_LIST,
            avg_pct[method],
            marker=MARKERS[method],
            linestyle=LINESTYLES[method],
            linewidth=2,
            color=COLORS[method],
            label=LABELS[method],
            zorder=5,
        )

    ax.set_xlabel("Interval for updating command value [sec]", fontsize=26, labelpad=10)
    ax.set_ylabel("Accuracy [%]", fontsize=26)
    ax.set_xticks(TAU_LIST)
    ax.tick_params(axis="x", labelsize=20, length=5)
    ax.tick_params(axis="y", labelsize=20, length=5)
    ax.set_ylim(0, 102)
    ax.yaxis.set_major_locator(plt.MultipleLocator(10))
    ax.yaxis.grid(True, linestyle="-", linewidth=0.8, alpha=1.0)
    ax.xaxis.grid(True, linestyle="-", alpha=0.5)
    ax.legend(fontsize=16, loc="lower right")

    fig.tight_layout()
    out_path = OUT_DIR / f"i_a_pure_extended_accuracy_ev_interval:{ev_int}s_line.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"Saved: {os.path.basename(out_path)}")


def main():
    for ev_int in EV_INTERVALS:
        avg = load_all(ev_int)
        print(f"[I-a] EV interval={ev_int}s")
        print(pd.DataFrame(avg, index=TAU_LIST))
        plot_line(avg, ev_int)


if __name__ == "__main__":
    main()
