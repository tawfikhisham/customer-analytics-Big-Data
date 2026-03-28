FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends bash && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pandas numpy matplotlib seaborn scikit-learn scipy requests openpyxl

WORKDIR /app/pipeline/
COPY ingest.py preprocess.py analytics.py visualize.py cluster.py summary.sh README.md /app/pipeline/

CMD ["/bin/bash"]
