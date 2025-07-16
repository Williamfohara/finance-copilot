# scripts/variance.py
import os

import matplotlib.pyplot as plt
import pandas as pd


def load_gl(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, parse_dates=["date"])
    df["year"] = df["date"].dt.year
    df["quarter"] = df["date"].dt.to_period("Q")
    return df


def load_account_list(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)


def enrich_with_account_metadata(gl_df: pd.DataFrame, account_df: pd.DataFrame) -> pd.DataFrame:
    enriched_df = gl_df.merge(
        account_df, left_on="split", right_on="account", how="left", suffixes=("", "_dim")
    )
    return enriched_df


def budget_vs_actual(df: pd.DataFrame, year: int) -> pd.DataFrame:
    df_year = df[df["year"] == year]

    # Split budget vs actual
    budget_df = df_year[df_year["transaction_type"] == "Budget"]
    actual_df = df_year[df_year["transaction_type"] != "Budget"]

    # Summarize budgets
    budget_summary = (
        budget_df.groupby(["split", "quarter"])["amount"].sum().reset_index(name="budget")
    )

    # Summarize actuals
    actual_summary = (
        actual_df.groupby(["split", "quarter"])["amount"].sum().reset_index(name="actual")
    )

    # Merge summaries
    merged = pd.merge(actual_summary, budget_summary, on=["split", "quarter"], how="outer").fillna(
        0
    )

    # Enrich with account metadata (using first non-null metadata found)
    metadata = df[["split", "parent_account", "type", "detail_type"]].drop_duplicates(
        subset=["split"]
    )
    merged = merged.merge(metadata, on="split", how="left")

    merged["variance"] = merged["actual"] - merged["budget"]
    return merged


def plot_variance(variance_df: pd.DataFrame, output_dir: str):
    for quarter, group in variance_df.groupby("quarter"):
        ax = group.plot(
            x="split", y=["budget", "actual"], kind="bar", title=f"Budget vs Actual - {quarter}"
        )
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        output_path = os.path.join(output_dir, f"budget_vs_actual_{quarter}.png")
        plt.savefig(output_path)
        plt.close()
        print(f"✅ Saved chart for {quarter} to {output_path}")


if __name__ == "__main__":
    gl_path = "clean_data/qbo_general_ledger.csv"
    account_list_path = "clean_data/qbo_account_list.csv"
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    df_gl = load_gl(gl_path)
    df_account = load_account_list(account_list_path)
    df_enriched = enrich_with_account_metadata(df_gl, df_account)

    bva = budget_vs_actual(df_enriched, 2025)
    print("\n📊 Budget vs Actual + Variance:\n", bva)

    # Save DataFrame to CSV
    csv_output_path = os.path.join(output_dir, "budget_vs_actual_variance.csv")
    bva.to_csv(csv_output_path, index=False)
    print(f"✅ Saved variance dataframe to {csv_output_path}")

    plot_variance(bva, output_dir)
