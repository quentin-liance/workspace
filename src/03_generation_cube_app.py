import pandas as pd

import paths

# Read the raw journal data from an Excel file, specifying all columns as strings
journal = pd.read_parquet(paths.JOURNAL_STRUCTURED_FILE_PATH)

# Read the processed plan comptable data from a Parquet file
compte_charges = pd.read_parquet(paths.COMPTE_CHARGES_STRUCTURED_FILE_PATH)

# Create a mask to filter rows where the "COMPTE" column starts with "6"
masque_charge = journal["COMPTE"].str[0] == "6"

# Use the mask to filter the journal dataframe and reset the index
charges = journal.loc[masque_charge].reset_index(drop=True)

# Create a new column "CLE" by taking the first 3 characters of the "COMPTE" column
charges["CLE"] = charges["COMPTE"].str[:3]
# Merge the 'charges' dataframe with the 'compte_charges' dataframe
# Perform a left join on the 'CLE' column from 'charges' and 'CODE_SOUS_CATEGORIE' column from 'compte_charges'
# Validate that each row in 'charges' matches at most one row in 'compte_charges'
charges_plan_de_compte = charges.merge(
    right=compte_charges,
    how="left",
    left_on="CLE",
    right_on="CODE_SOUS_CATEGORIE",
    validate="m:1",
)
# Drop the specified columns from the 'charges_plan_de_compte' dataframe
charges_plan_de_compte = charges_plan_de_compte.drop(
    columns=[
        "CLE",  # Drop the 'CLE' column
        "CODE_SOUS_CATEGORIE",  # Drop the 'CODE_SOUS_CATEGORIE' column
        "JOURNAL",  # Drop the 'JOURNAL' column
        "CREDIT",  # Drop the 'CREDIT' column
        "ECHEANCE",  # Drop the 'ECHEANCE' column
        "PIECE",  # Drop the 'PIECE' column
        "REF_PIECE",  # Drop the 'REF_PIECE' column
        "COMPTE",  # Drop the 'COMPTE' column
    ],
    axis=1,  # Specify that we are dropping columns (not rows)
).filter(
    [
        "DATE",
        "LIBELLE_CATEGORIE",
        "LIBELLE_SOUS_CATEGORIE",
        "LIBELLE",
        "DEBIT",
        "DATE_STR",
    ]
)  # Keep only the specified columns

# Save the 'charges_plan_de_compte' dataframe to a Parquet file
# The file path is specified by 'paths.CUBE_FILE_PATH'
# The 'index=False' parameter ensures that the index is not saved in the file
charges_plan_de_compte.to_parquet(paths.CUBE_FILE_PATH, index=False)
