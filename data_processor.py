import pandas as pd
import json
import os

def load_dataset(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        return pd.read_csv(file_path)
    elif ext == '.json':
        with open(file_path) as f:
            return json.load(f)
    elif ext == '.jsonl':
        with open(file_path) as f:
            return [json.loads(line) for line in f]
    else:
        raise ValueError(f"Unsupported format: {ext}")

def validate_dataset(data, task='sft'):
    if task == 'sft':
        required_keys = ['instruction', 'output']
    elif task == 'dpo':
        required_keys = ['prompt', 'chosen', 'rejected']
    else:
        required_keys = []

    if isinstance(data, list) and len(data) > 0:
        missing = [k for k in required_keys if k not in data[0]]
        if missing:
            return False, f"Missing keys: {missing}"
    return True, "Valid"
