import os
import sys
import pandas as pd
from sklearn.cluster import KMeans


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cluster.py <csv-path>")
        sys.exit(1)

    input_path = sys.argv[1]
    df = pd.read_csv(input_path)

    cluster_features = ["pca_1", "pca_2", "pca_3"]
    model = KMeans(n_clusters=3, random_state=42, n_init=10)
    df["cluster"] = model.fit_predict(df[cluster_features])

    cluster_counts = df["cluster"].value_counts().sort_index()
    output_txt = os.path.join(os.getcwd(), "clusters.txt")
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("K-Means clustering summary (k=3)\n")
        for cluster_id, count in cluster_counts.items():
            f.write(f"Cluster {cluster_id}: {count} customers\n")

    df.to_csv(os.path.join(os.getcwd(), "clustered_customers.csv"), index=False)

    print("Clustering completed successfully.")
    print(cluster_counts.to_string())
