import pandas as pd

import paths
from utils import clean_col_names

# Read the raw journal data from an Excel file, specifying all columns as strings
journal = pd.read_excel(io=paths.JOURNAL_RAW_FILE_PATH, dtype=str)

# Clean the column names of the journal dataframe using the clean_col_names function
journal.columns = clean_col_names(journal)

# Convert the columns "DEBIT" and "CREDIT" to float type
for col in ["DEBIT", "CREDIT"]:
    journal[col] = journal[col].astype(float)

journal["DATE_STR"] = journal["DATE"]

# Convert the columns "DATE" and "ECHEANCE" to datetime type with the specified format
for col in ["DATE", "ECHEANCE"]:
    journal[col] = pd.to_datetime(journal[col], format="%d/%m/%Y")

# Create a new column "AAAAMM" by formatting the "DATE" column to "YYYYMM"

# Save the cleaned journal data to a parquet file
journal.to_parquet(paths.JOURNAL_STRUCTURED_FILE_PATH, index=False)
