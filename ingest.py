import io
import os
import sys
import zipfile
import subprocess
from typing import Optional

import pandas as pd


SUPPORTED_EXTENSIONS = {'.csv', '.tsv', '.json', '.xlsx', '.xls', '.zip'}


def _read_tabular_from_bytes(filename: str, data: bytes) -> pd.DataFrame:
    lower = filename.lower()
    buffer = io.BytesIO(data)

    if lower.endswith('.csv'):
        return pd.read_csv(buffer)
    if lower.endswith('.tsv'):
        return pd.read_csv(buffer, sep='\t')
    if lower.endswith('.json'):
        return pd.read_json(buffer)
    if lower.endswith('.xlsx') or lower.endswith('.xls'):
        return pd.read_excel(buffer)

    raise ValueError(f"Unsupported file inside ZIP archive: {filename}")


def _find_dataset_inside_zip(zip_path: str) -> tuple[str, pd.DataFrame]:
    preferred_extensions = ('.xlsx', '.xls', '.csv', '.tsv', '.json')

    with zipfile.ZipFile(zip_path, 'r') as archive:
        members = [
            name for name in archive.namelist()
            if not name.endswith('/') and name.lower().endswith(preferred_extensions)
        ]

        if not members:
            raise ValueError(
                'ZIP archive does not contain a supported dataset file '
                '(.xlsx, .xls, .csv, .tsv, .json).'
            )

        priority_map = {ext: idx for idx, ext in enumerate(preferred_extensions)}
        members.sort(key=lambda name: (priority_map[os.path.splitext(name.lower())[1]], len(name)))
        selected_member = members[0]

        with archive.open(selected_member) as extracted:
            data = extracted.read()

    return selected_member, _read_tabular_from_bytes(selected_member, data)


def read_dataset(dataset_path: str) -> tuple[pd.DataFrame, str]:
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    lower = dataset_path.lower()
    extension = os.path.splitext(lower)[1]
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            'Unsupported dataset format. Please provide a CSV, TSV, JSON, XLSX, XLS, '
            'or the original ZIP dataset file.'
        )

    if lower.endswith('.csv'):
        return pd.read_csv(dataset_path), dataset_path
    if lower.endswith('.tsv'):
        return pd.read_csv(dataset_path, sep='\t'), dataset_path
    if lower.endswith('.json'):
        return pd.read_json(dataset_path), dataset_path
    if lower.endswith('.xlsx') or lower.endswith('.xls'):
        return pd.read_excel(dataset_path), dataset_path
    if lower.endswith('.zip'):
        inner_name, df = _find_dataset_inside_zip(dataset_path)
        source_description = f"{dataset_path} -> {inner_name}"
        return df, source_description

    raise ValueError(
        'Unsupported dataset format. Please provide a CSV, TSV, JSON, XLSX, XLS, '
        'or the original ZIP dataset file.'
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <dataset-path>")
        sys.exit(1)

    dataset_path = sys.argv[1]
    df, source_description = read_dataset(dataset_path)

    output_path = os.path.join(os.getcwd(), 'data_raw.csv')
    df.to_csv(output_path, index=False)

    print(f"Loaded dataset from: {source_description}")
    print(f"Saved raw copy to: {output_path}")
    print(f"Shape: {df.shape}")

    subprocess.run([sys.executable, 'preprocess.py', output_path], check=True)
