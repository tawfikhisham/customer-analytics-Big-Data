import os
import sys
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python visualize.py <csv-path>")
        sys.exit(1)

    input_path = sys.argv[1]
    df = pd.read_csv(input_path)
    sns.set_theme(style="whitegrid")

    fig, axes = plt.subplots(1, 3, figsize=(21, 7))
    fig.suptitle("Customer Analytics – Summary Dashboard", fontsize=16, fontweight="bold", y=1.01)

    # Plot 1: Spend distribution (log scale because data is heavily right-skewed)
    axes[0].hist(df["total_spend"], bins=40, color="#4C72B0", edgecolor="white", linewidth=0.5)
    axes[0].set_yscale("log")
    axes[0].set_title("Customer Spend Distribution", fontsize=12)
    axes[0].set_xlabel("Total Spend (£)", fontsize=10)
    axes[0].set_ylabel("Number of Customers (log scale)", fontsize=10)

    # Plot 2: Box plot — spread of order counts within each spend segment
    seg_order = ["Low", "Medium", "High"]
    sns.boxplot(data=df, x="spend_segment", y="order_count", order=seg_order,
                hue="spend_segment", palette="Set2", legend=False, ax=axes[1])
    axes[1].set_title("Order Count by Spend Segment", fontsize=12)
    axes[1].set_xlabel("Spend Segment", fontsize=10)
    axes[1].set_ylabel("Number of Orders", fontsize=10)

    # Plot 3: Top 10 countries by customer count (UK highlighted)
    country_counts = (
        df.groupby("dominant_country")["CustomerID"]
        .count()
        .sort_values(ascending=False)
        .head(10)
    )
    bar_colors = [
        "#DD8452" if c == "United Kingdom" else "#4C72B0"
        for c in country_counts.index[::-1]
    ]
    axes[2].barh(country_counts.index[::-1], country_counts.values[::-1],
                 color=bar_colors, edgecolor="white", linewidth=0.5)
    axes[2].set_title("Top 10 Countries by Customer Count", fontsize=12)
    axes[2].set_xlabel("Number of Customers", fontsize=10)
    axes[2].set_ylabel("Country", fontsize=10)

    plt.tight_layout()
    output_path = os.path.join(os.getcwd(), "summary_plot.png")
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved summary visualization to: {output_path}")
    subprocess.run([sys.executable, "cluster.py", input_path], check=True)
