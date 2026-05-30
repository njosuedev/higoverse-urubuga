import pandas as pd


required_columns = [
    "Product Name",
    "Sale Price",
    "Sale Quantity",
    "Customer Name"
]



def clean_value(v):

    if v is None:
        return None

    if pd.isna(v):
        return None

    v = str(v).strip()

    if v.lower() in ["nan", "none", "null", ""]:
        return None

    return v



def normalize_columns(df: pd.DataFrame):

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("_", " ")
        .str.title()
    )

    return df