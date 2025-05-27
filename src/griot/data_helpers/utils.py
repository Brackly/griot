import pandas as pd

def load_data(path: str, dataset_type: str = "pandas"):
    if dataset_type == 'pandas':
        return pd.read_csv(path)
    else:
        raise ValueError(f"Unsupported dataset type: {dataset_type}. Supported types are: 'pandas'.")

