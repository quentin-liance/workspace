import pandas as pd


def clean_col_names(df: pd.DataFrame) -> list[str]:
    new_column_names = [
        col.strip()
        .upper()
        .replace(" ", "")
        .replace(".", "_")
        .replace("É", "E")
        .replace("È", "E")
        for col in df.columns
    ]

    return new_column_names


def currency_formating(number: float) -> str:
    return f"{number:,.0f} €".replace(",", " ")
