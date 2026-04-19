import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator


ROOT_DIR = Path(__file__).resolve().parents[3]
CASE_ACC_DIR = ROOT_DIR / "case_study/sensitivity_analysis/ii-d_Time_delay_from_command_value_to_EV_current/accuracy"
PURE_ACC_DIR = Path(__file__).resolve().parent / "accuracy"
OUT_DIR = Path(__file__).resolve().parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

METHODS = [
    ("Correlation-Euclidean", "Cor-Euc", "#228b22", "s"),
    ("Correlation-DTW", "Cor-DTW", "#ff8c00", "o"),
    ("Baseline (Correlation)", "Cor", "#376ea4", "^"),
    ("Pure Euclidean", "Pure-Euc", "#a23ecf", "D"),
    ("Pure DTW", "Pure-DTW", "#d84b5b", "x"),
]


def load_case_data(interval: int, metric_key: str) -> pd.DataFrame:
    return pd.read_csv(CASE_ACC_DIR / f"300_{interval}interval_{metric_key}_accuracy.csv")


def load_pure_data(interval: int, metric_key: str) -> pd.DataFrame:
    return pd.read_csv(PURE_ACC_DIR / f"300_{interval}interval_{metric_key}_accuracy.csv")


def _x_col(df: pd.DataFrame) -> str:
    return "command_ev_samplingTime_diff" if "command_ev_samplingTime_diff" in df.columns else "time_delay_II-d"


def _y_col(df: pd.DataFrame) -> str:
    return "Matching_accuracy" if "Matching_accuracy" in df.columns else "pairing_accuracy"


def plot_single(interval: int, data_map: dict[str, pd.DataFrame], filename: str) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))

    for label, metric_key, color, marker in METHODS:
        df = data_map[metric_key]
        ax.plot(
            df[_x_col(df)],
            df[_y_col(df)] * 100,
            marker=marker,
            linewidth=2,
            color=color,
            linestyle="-" if "Pure" in label else ("dashed" if label == "Baseline (Correlation)" else "-"),
            label=label,
        )

    ax.set_xlabel("Time delay from command value to EV current measurement [sec]", fontsize=23, labelpad=10)
    ax.set_ylabel("Accuracy [%]", fontsize=26, labelpad=0)
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(10))
    ax.tick_params(axis="x", which="major", labelsize=20, length=5)
    ax.tick_params(axis="x", which="minor", labelsize=0, length=5)
    ax.tick_params(axis="y", which="major", labelsize=20, length=5)
    ax.tick_params(axis="y", which="minor", labelsize=0, length=5)
    ax.grid(which="major", linestyle="-", linewidth=0.8, alpha=1)
    ax.grid(which="minor", linestyle="-", linewidth=0.8, alpha=1)
    ax.set_xlim(0, 29)
    ax.set_ylim(0, 102)
    ax.legend(loc="lower right", fontsize=15)

    plt.tight_layout()
    out_path = OUT_DIR / filename
    fig.savefig(out_path)
    plt.close(fig)
    print(f"Saved: {os.path.basename(out_path)}")


def plot_combined(data30: dict[str, pd.DataFrame], data60: dict[str, pd.DataFrame], filename: str) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))

    for label, metric_key, color, marker in METHODS:
        df30 = data30[metric_key]
        df60 = data60[metric_key]

        ax.plot(
            df30[_x_col(df30)],
            df30[_y_col(df30)] * 100,
            marker=marker,
            linewidth=2,
            linestyle="-",
            color=color,
            label=f"{label} (EV interval: 30s)",
        )
        ax.plot(
            df60[_x_col(df60)],
            df60[_y_col(df60)] * 100,
            marker=marker,
            linewidth=2,
            linestyle="--",
            color=color,
            label=f"{label} (EV interval: 60s)",
        )

    ax.set_xlabel("Time delay from command value to EV current measurement [sec]", fontsize=23, labelpad=10)
    ax.set_ylabel("Accuracy [%]", fontsize=26, labelpad=0)
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(10))
    ax.tick_params(axis="x", which="major", labelsize=20, length=5)
    ax.tick_params(axis="x", which="minor", labelsize=0, length=5)
    ax.tick_params(axis="y", which="major", labelsize=20, length=5)
    ax.tick_params(axis="y", which="minor", labelsize=0, length=5)
    ax.grid(which="major", linestyle="-", linewidth=0.8, alpha=1)
    ax.grid(which="minor", linestyle="-", linewidth=0.8, alpha=1)
    ax.set_xlim(0, 29)
    ax.set_ylim(0, 102)
    ax.legend(loc="lower right", fontsize=11, ncol=1)

    plt.tight_layout()
    out_path = OUT_DIR / filename
    fig.savefig(out_path)
    plt.close(fig)
    print(f"Saved: {os.path.basename(out_path)}")


def main():
    data_30 = {
        "Cor-Euc": load_case_data(30, "Cor-Euc"),
        "Cor-DTW": load_case_data(30, "Cor-DTW"),
        "Cor": load_case_data(30, "Cor"),
        "Pure-Euc": load_pure_data(30, "Pure-Euc"),
        "Pure-DTW": load_pure_data(30, "Pure-DTW"),
    }
    data_60 = {
        "Cor-Euc": load_case_data(60, "Cor-Euc"),
        "Cor-DTW": load_case_data(60, "Cor-DTW"),
        "Cor": load_case_data(60, "Cor"),
        "Pure-Euc": load_pure_data(60, "Pure-Euc"),
        "Pure-DTW": load_pure_data(60, "Pure-DTW"),
    }

    plot_single(30, data_30, "ii_d_pure_extended_ev_interval:30s.png")
    plot_single(60, data_60, "ii_d_pure_extended_ev_interval:60s.png")
    plot_combined(data_30, data_60, "ii_d_pure_extended_all.png")


if __name__ == "__main__":
    main()
