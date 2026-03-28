#!/bin/bash
set -e

CONTAINER_NAME=${1:-customer-analytics-container}
PROJECT_DIR=$(cd "$(dirname "$0")" && pwd)
RESULTS_DIR="$PROJECT_DIR/results"

mkdir -p "$RESULTS_DIR"

CONTAINER_ID=$(docker ps -aq -f "name=^${CONTAINER_NAME}$")

if [ -z "$CONTAINER_ID" ]; then
  echo "Error: container '$CONTAINER_NAME' was not found."
  exit 1
fi

OUTPUT_FILES=(
  "data_raw.csv"
  "data_preprocessed.csv"
  "clustered_customers.csv"
  "insight1.txt"
  "insight2.txt"
  "insight3.txt"
  "summary_plot.png"
  "clusters.txt"
)

echo "Copying generated outputs from container to: $RESULTS_DIR"
for file in "${OUTPUT_FILES[@]}"; do
  docker cp "$CONTAINER_ID:/app/pipeline/$file" "$RESULTS_DIR/$file"
done

if docker ps -q -f "id=$CONTAINER_ID" >/dev/null && [ -n "$(docker ps -q -f "id=$CONTAINER_ID")" ]; then
  docker stop "$CONTAINER_ID" >/dev/null
fi

docker rm "$CONTAINER_ID" >/dev/null

echo "Done. Outputs copied and container removed successfully."
