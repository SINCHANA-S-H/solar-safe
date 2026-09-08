import os
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# SolarSafe AI V2 — Results Visualization
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

V2_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "experiments",
    "v2"
)

COMPARISON_CSV = os.path.join(
    V2_DIR,
    "model_comparison.csv"
)

HARD_CC_CSV = os.path.join(
    V2_DIR,
    "hard_cell_crack_comparison.csv"
)

GRAPH_DIR = os.path.join(
    V2_DIR,
    "graphs"
)


# ============================================================
# Utility Functions
# ============================================================

def setup_output_directory():
    """Create graph output directory if it does not exist."""
    os.makedirs(GRAPH_DIR, exist_ok=True)


def load_comparison_data():
    """Load model comparison CSV."""

    print("\nLoading comparison CSV:")
    print(COMPARISON_CSV)

    if not os.path.exists(COMPARISON_CSV):
        raise FileNotFoundError(
            f"\n[ERROR] Comparison CSV not found:\n{COMPARISON_CSV}"
        )

    df = pd.read_csv(COMPARISON_CSV)

    print("\n[OK] Comparison data loaded.")

    print("\nColumns found:")
    print(list(df.columns))

    print("\nModel Results:")
    print(df.to_string(index=False))

    return df


# ============================================================
# Plot 1 — Overall Performance
# ============================================================

def plot_overall_performance(df):

    print("\nCreating overall performance comparison...")

    models = df["model"]

    metrics = [
        "accuracy",
        "macro_f1",
        "weighted_f1"
    ]

    labels = [
        "Accuracy",
        "Macro F1",
        "Weighted F1"
    ]

    available_metrics = [
        metric for metric in metrics
        if metric in df.columns
    ]

    if not available_metrics:
        print("[WARN] Required overall performance metrics not found.")
        return

    plot_df = df[["model"] + available_metrics]

    ax = plot_df.set_index("model").plot(
        kind="bar",
        figsize=(10, 6)
    )

    ax.set_title("Overall Model Performance Comparison")
    ax.set_xlabel("Model")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)

    ax.legend(labels[:len(available_metrics)])

    plt.xticks(rotation=0)
    plt.tight_layout()

    output_path = os.path.join(
        GRAPH_DIR,
        "overall_performance_comparison.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"[OK] Saved: {output_path}")


# ============================================================
# Plot 2 — Cell_Crack Performance
# ============================================================

def plot_cell_crack_performance(df):

    print("\nCreating Cell_Crack performance comparison...")

    required_columns = [
        "cell_crack_precision",
        "cell_crack_recall",
        "cell_crack_f1"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        print(
            "[WARN] Missing Cell_Crack columns:",
            missing_columns
        )
        return

    plot_df = df[
        [
            "model",
            "cell_crack_precision",
            "cell_crack_recall",
            "cell_crack_f1"
        ]
    ]

    ax = plot_df.set_index("model").plot(
        kind="bar",
        figsize=(10, 6)
    )

    ax.set_title("Cell_Crack Detection Performance")
    ax.set_xlabel("Model")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)

    ax.legend(
        [
            "Precision",
            "Recall",
            "F1 Score"
        ]
    )

    plt.xticks(rotation=0)
    plt.tight_layout()

    output_path = os.path.join(
        GRAPH_DIR,
        "cell_crack_performance.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"[OK] Saved: {output_path}")


# ============================================================
# Plot 3 — Cell_Crack → Normal Errors
# ============================================================

def plot_cell_crack_to_normal_errors(df):

    print(
        "\nCreating Cell_Crack → Normal error comparison..."
    )

    error_column = "cell_crack_pred_as_normal"

    if error_column not in df.columns:

        print(
            f"[WARN] Could not find required column: "
            f"{error_column}"
        )

        print(
            "Available columns:",
            list(df.columns)
        )

        return

    models = df["model"]
    errors = df[error_column]

    plt.figure(figsize=(9, 6))

    bars = plt.bar(
        models,
        errors
    )

    plt.title(
        "Cell_Crack → Normal Misclassification Errors"
    )

    plt.xlabel("Model")

    plt.ylabel(
        "Number of Cell_Crack Images Predicted as Normal"
    )

    plt.xticks(rotation=0)

    # Add values above bars
    for bar, value in zip(bars, errors):

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            str(int(value)),
            ha="center",
            va="bottom",
            fontsize=11
        )

    plt.tight_layout()

    output_path = os.path.join(
        GRAPH_DIR,
        "cell_crack_to_normal_errors.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"[OK] Saved: {output_path}")


# ============================================================
# Plot 4 — Hard Cell_Crack Recovery Summary
# ============================================================

def plot_hard_cell_crack_recovery():

    print(
        "\nCreating hard Cell_Crack recovery comparison..."
    )

    if not os.path.exists(HARD_CC_CSV):

        print(
            "[WARN] Hard Cell_Crack comparison CSV not found."
        )

        return

    hard_df = pd.read_csv(HARD_CC_CSV)

    print(
        "[OK] Hard Cell_Crack comparison data loaded."
    )

    print("Columns:")
    print(list(hard_df.columns))

    required_columns = [
        "v1_prediction",
        "v2a_prediction",
        "v2b_prediction"
    ]

    missing = [
        col for col in required_columns
        if col not in hard_df.columns
    ]

    if missing:

        print(
            "[WARN] Missing prediction columns:",
            missing
        )

        return

    # Hard samples are V1 Cell_Crack images
    # misclassified by V1 as Normal.
    total_hard_samples = len(hard_df)

    if total_hard_samples == 0:

        print(
            "[WARN] No hard Cell_Crack samples found."
        )

        return

    v1_recovered = (
        hard_df["v1_prediction"]
        == "Cell_Crack"
    ).sum()

    v2a_recovered = (
        hard_df["v2a_prediction"]
        == "Cell_Crack"
    ).sum()

    v2b_recovered = (
        hard_df["v2b_prediction"]
        == "Cell_Crack"
    ).sum()

    models = [
        "V1 Baseline",
        "V2-A Augmentation",
        "V2-B Focal Loss"
    ]

    recovered_counts = [
        v1_recovered,
        v2a_recovered,
        v2b_recovered
    ]

    plt.figure(figsize=(9, 6))

    bars = plt.bar(
        models,
        recovered_counts
    )

    plt.title(
        "Hard Cell_Crack Recovery Comparison"
    )

    plt.xlabel("Model")

    plt.ylabel(
        f"Recovered Hard Cell_Crack Samples "
        f"(out of {total_hard_samples})"
    )

    plt.ylim(
        0,
        max(total_hard_samples, max(recovered_counts)) + 1
    )

    for bar, value in zip(
        bars,
        recovered_counts
    ):

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.1,
            str(int(value)),
            ha="center",
            va="bottom",
            fontsize=11
        )

    plt.tight_layout()

    output_path = os.path.join(
        GRAPH_DIR,
        "hard_cell_crack_recovery.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"[OK] Saved: {output_path}")


# ============================================================
# Plot 5 — Model Metric Profile
# ============================================================

def plot_model_metric_profile(df):

    print(
        "\nCreating metric profile comparison..."
    )

    metric_columns = [
        "accuracy",
        "macro_precision",
        "macro_recall",
        "macro_f1",
        "weighted_f1"
    ]

    available_metrics = [
        metric for metric in metric_columns
        if metric in df.columns
    ]

    if not available_metrics:

        print(
            "[WARN] No metric profile columns found."
        )

        return

    plot_df = df[
        ["model"] + available_metrics
    ]

    ax = plot_df.set_index("model").T.plot(
        kind="line",
        marker="o",
        figsize=(11, 7)
    )

    ax.set_title("Model Performance Metric Profile")

    ax.set_xlabel("Metric")

    ax.set_ylabel("Score")

    ax.set_ylim(0, 1.05)

    ax.legend(
        title="Model"
    )

    plt.xticks(rotation=30)

    plt.tight_layout()

    output_path = os.path.join(
        GRAPH_DIR,
        "model_metric_profile.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"[OK] Saved: {output_path}")


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 65)

    print(
        "SolarSafe AI V2 — Results Visualization"
    )

    print("=" * 65)

    setup_output_directory()

    # --------------------------------------------------------
    # Load comparison data
    # --------------------------------------------------------

    df = load_comparison_data()

    # --------------------------------------------------------
    # Create graphs
    # --------------------------------------------------------

    plot_overall_performance(df)

    plot_cell_crack_performance(df)

    plot_cell_crack_to_normal_errors(df)

    plot_hard_cell_crack_recovery()

    plot_model_metric_profile(df)

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print("\n" + "=" * 65)

    print(
        "[DONE] All V2 result plots created successfully."
    )

    print(
        "Output directory:"
    )

    print(GRAPH_DIR)

    print("=" * 65)


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":
    main()