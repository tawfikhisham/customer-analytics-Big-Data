# Customer Analytics Pipeline - CSCI461 Assignment 1

## Team Members

* Tawfik Hisham Tawfik – 221001918
* Ahmed Abdelsameea Mahmoud – 202001427
* Nada Gamal Zaki – 221000829

---

## Project Overview

This project implements a complete customer analytics pipeline using Docker. The pipeline starts with a raw dataset and goes through multiple stages including data cleaning, preprocessing, analysis, visualization, and finally clustering.

Each step passes its output to the next one, forming a continuous workflow from raw data to final insights.

---

## Dataset Used

We used the Online Retail dataset from the UCI Machine Learning Repository.

Original file format:

* `Online Retail.xlsx`

---

## Supported Input Formats

The pipeline supports multiple file formats:

* CSV
* TSV
* JSON
* Excel (xlsx / xls)
* ZIP

This allows the system to work with different dataset formats as long as they follow the expected structure.

---

## Expected Dataset Columns

The dataset must include the following columns:

* InvoiceNo
* StockCode
* Description
* Quantity
* InvoiceDate
* UnitPrice
* CustomerID
* Country

---

## Folder Structure

```text
customer-analytics/
├── Dockerfile
├── ingest.py
├── preprocess.py
├── analytics.py
├── visualize.py
├── cluster.py
├── summary.sh
├── README.md
└── results/
```

---

## What Each File Does

### Dockerfile

* Sets up the environment using Python 3.11
* Installs required libraries
* Defines the working directory
* Prepares the container for execution

---

### ingest.py

* Reads the dataset path from the user
* Loads the dataset
* Saves a raw copy as `data_raw.csv`
* Calls the preprocessing step

---

### preprocess.py

Handles all preprocessing tasks:

* Data cleaning
* Handling missing values
* Feature engineering
* Dimensionality reduction using PCA
* Data segmentation

---

### analytics.py

* Generates basic insights from the data
* Saves results as text files

---

### visualize.py

* Creates visual representations of the data
* Saves plots as image files

---

### cluster.py

* Applies K-Means clustering with k = 3
* Groups customers into clusters

---

### summary.sh

* Copies results from the container to the host machine
* Stops and removes the container

---

## Preprocessing Summary

### Data Cleaning

* Removed duplicate rows
* Handled missing values
* Removed cancelled transactions
* Filtered invalid values (e.g., negative quantity or price)

---

### Feature Transformation

* Converted CustomerID to integer
* Created a new feature (LineTotal)
* Extracted date-related features
* Aggregated data at the customer level
* Applied scaling to numeric features

---

### Dimensionality Reduction

* Selected relevant features
* Applied PCA
* Reduced data to 3 components

---

### Discretization

Customers were categorized based on:

* Spending level
* Purchase frequency
* Recency

---

## Execution Flow

```text
ingest → preprocess → analytics → visualize → cluster
```

---

## Docker Commands

### Build Image

```bash
docker build -t customer-analytics-image .
```

---

### Run Container (PowerShell)

```powershell
docker run -it --name customer-analytics-container -v "${PWD}:/workspace" customer-analytics-image
```

---

### Start Pipeline

```bash
python ingest.py "/workspace/Online Retail.xlsx"
```

---

### Exit Container

```bash
exit
```

---

### Copy Results

```cmd
docker cp customer-analytics-container:/app/pipeline/data_raw.csv .\results\
```

(Repeat for other output files)

---

## Sample Outputs

### Insight Example

```text
Total customers: 4338
Average spend: 2048.69
```

---

### Clustering Example

```text
Cluster 0: 2678
Cluster 1: 1643
Cluster 2: 17
```

---

## Output Files

After execution, the following files will be generated:

* data_raw.csv
* data_preprocessed.csv
* clustered_customers.csv
* insight1.txt
* insight2.txt
* insight3.txt
* summary_plot.png
* clusters.txt

---

