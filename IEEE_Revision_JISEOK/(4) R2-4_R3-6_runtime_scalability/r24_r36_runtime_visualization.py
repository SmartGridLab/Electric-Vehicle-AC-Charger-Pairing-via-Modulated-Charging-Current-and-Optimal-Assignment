from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator


BASE_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = BASE_DIR / "runtime"
FIG_DIR = BASE_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_PATH = RUNTIME_DIR / "r24_r36_runtime_summary.csv"

METHOD_STYLES = {
    "Correlation": {"color": "#376ea4", "marker": "^"},
    "Correlation+DTW": {"color": "#ff8c00", "marker": "o"},
    "Correlation+Euclidean": {"color": "#228b22", "marker": "s"},
    "Pure-DTW": {"color": "#8b1a1a", "marker": "D"},
    "Pure-Euclidean": {"color": "#6a5acd", "marker": "v"},
}


def _plot_total(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    for method in METHOD_STYLES:
        part = df[df["method"] == method].sort_values("num_patterns")
        if part.empty:
            continue
        style = METHOD_STYLES[method]
        ax.plot(
            part["num_patterns"],
            part["total_sec_mean"],
            marker=style["marker"],
            linewidth=2,
            color=style["color"],
            label=method,
        )

    ax.set_xlabel("pairs [unit]", fontsize=22)
    ax.set_ylabel("time [sec]", fontsize=22)
    ax.tick_params(axis="x", labelsize=16, length=5)
    ax.tick_params(axis="y", labelsize=16, length=5)
    y_max = float(df["total_sec_mean"].max()) if not df.empty else 100.0
    if y_max <= 200:
        step = 20
    elif y_max <= 600:
        step = 50
    else:
        step = 100
    ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.grid(axis="y", which="major", linestyle="-", linewidth=0.8, alpha=0.6)
    ax.legend(loc="upper left", fontsize=14)
    plt.tight_layout()
    out_path = FIG_DIR / "r24_r36_runtime_total_vs_pairs.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"Saved: {out_path}")


def _plot_breakdown(df: pd.DataFrame) -> None:
    methods = [m for m in METHOD_STYLES if m in set(df["method"])]
    if not methods:
        return

    fig, axes = plt.subplots(1, len(methods), figsize=(6 * len(methods), 5), sharey=True)
    if len(methods) == 1:
        axes = [axes]

    for ax, method in zip(axes, methods):
        part = df[df["method"] == method].sort_values("num_patterns")
        style = METHOD_STYLES[method]
        ax.plot(
            part["num_patterns"],
            part["cost_matrix_sec_mean"],
            marker=style["marker"],
            linewidth=2,
            color=style["color"],
            label="cost matrix",
        )
        ax.plot(
            part["num_patterns"],
            part["assignment_sec_mean"],
            marker=style["marker"],
            linewidth=2,
            linestyle="dashed",
            color="#7a7a7a",
            label="assignment",
        )
        ax.set_title(method, fontsize=13)
        ax.set_xlabel("pairs [unit]", fontsize=14)
        ax.grid(which="major", linestyle="-", linewidth=0.8, alpha=1)
        ax.tick_params(axis="x", labelsize=12, length=4)
        ax.tick_params(axis="y", labelsize=12, length=4)
        ax.legend(loc="upper left", fontsize=10)

    axes[0].set_ylabel("time [sec]", fontsize=14)
    plt.tight_layout()
    out_path = FIG_DIR / "r24_r36_runtime_breakdown_vs_pairs.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"Saved: {out_path}")


def main() -> None:
    if not SUMMARY_PATH.exists():
        raise FileNotFoundError(
            f"Runtime summary not found: {SUMMARY_PATH}. Run r24_r36_runtime_measurement.py first."
        )
    df = pd.read_csv(SUMMARY_PATH)
    _plot_total(df)
    _plot_breakdown(df)


if __name__ == "__main__":
    main()
