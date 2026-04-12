from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator


ROOT_DIR = Path(__file__).resolve().parents[2]
CASE_ACC_DIR = ROOT_DIR / "case_study/scalability_analysis/accuracy"
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


def load_case(metric_key: str, regime: str, start_time: int) -> pd.DataFrame:
    return pd.read_csv(CASE_ACC_DIR / f"{metric_key}_{regime}_EV_start_time:{start_time}.csv")


def load_pure(metric_key: str, regime: str, start_time: int) -> pd.DataFrame:
    return pd.read_csv(PURE_ACC_DIR / f"{metric_key}_{regime}_EV_start_time:{start_time}.csv")


def y_col(df: pd.DataFrame) -> str:
    return "Matching_accuracy" if "Matching_accuracy" in df.columns else "pairing_accuracy"


def main():
    data_transient = {
        "Cor-Euc": load_case("Cor-Euc", "transient", 5),
        "Cor-DTW": load_case("Cor-DTW", "transient", 5),
        "Cor": load_case("Cor", "transient", 5),
        "Pure-Euc": load_pure("Pure-Euc", "transient", 5),
        "Pure-DTW": load_pure("Pure-DTW", "transient", 5),
    }
    data_steady = {
        "Cor-Euc": load_case("Cor-Euc", "steady", 25),
        "Cor-DTW": load_case("Cor-DTW", "steady", 25),
        "Cor": load_case("Cor", "steady", 25),
        "Pure-Euc": load_pure("Pure-Euc", "steady", 25),
        "Pure-DTW": load_pure("Pure-DTW", "steady", 25),
    }

    fig, ax = plt.subplots(figsize=(12, 8))

    for label, key, color, marker in METHODS:
        dft = data_transient[key]
        dfs = data_steady[key]

        ax.plot(
            dft["num_patterns"],
            dft[y_col(dft)] * 100,
            marker=marker,
            linestyle="dashed",
            linewidth=2,
            color=color,
            label=f"{label} (transient)",
        )
        ax.plot(
            dfs["num_patterns"],
            dfs[y_col(dfs)] * 100,
            marker=marker,
            linestyle="-",
            linewidth=2,
            color=color,
            label=f"{label} (steady)",
        )

    ax.set_xlabel("Number of EV-charger pairs", fontsize=24)
    ax.set_ylabel("Accuracy [%]", fontsize=24)
    ax.tick_params(axis="x", labelsize=16, length=5)
    ax.tick_params(axis="y", labelsize=16, length=5)
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.grid(which="major", linestyle="-", linewidth=0.8, alpha=1)
    ax.set_ylim(0, 102)
    ax.legend(loc="center right", fontsize=11)

    plt.tight_layout()
    out_path = OUT_DIR / "scale_pure_extended_accuracy_all.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
