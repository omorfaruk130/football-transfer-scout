"""
Converts an uploaded CSV into text documents suitable for embedding.
Each row becomes one readable text chunk — e.g. "Name: X, Age: Y, Club: Z, ..."
"""

import pandas as pd
import io


def csv_to_documents(uploaded_file) -> list[dict]:
    """
    uploaded_file: a Streamlit UploadedFile object (or any file-like object).
    Returns [{"source": filename, "chunk": text, "row_id": int}, ...]
    """
    df = pd.read_csv(uploaded_file)
    filename = getattr(uploaded_file, "name", "uploaded.csv")

    documents = []
    for i, row in df.iterrows():
        # Turn a row like {"name": "X", "age": 24, ...} into readable text
        text = ", ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
        documents.append({"source": filename, "chunk": text, "row_id": int(i)})

    return documents