import pandas as pd

import paths

# Read the Excel file specified by the path in paths.PLAN_COMPTABLE_RAW_FILE_PATH into a pandas DataFrame
# The dtype parameter ensures that all columns are read as strings
plan_comptable = pd.read_excel(paths.PLAN_COMPTABLE_RAW_FILE_PATH, dtype=str)

# Rename the columns of the DataFrame to "CODE" and "LIBELLE"
plan_comptable.columns = ["CODE", "LIBELLE"]

# Create a mask to filter rows where the first character of the "CODE" column is "6"
masque_compte_charges = plan_comptable["CODE"].str[0] == "6"  # noqa: E731

# Create a mask to filter rows where the length of the "CODE" column is 2
masque_categorie = plan_comptable["CODE"].str.len() == 2  # noqa: E731

# Create a mask to filter rows where the length of the "CODE" column is 3
masque_sous_categorie = plan_comptable["CODE"].str.len() == 3  # noqa: E731

# Filter the plan_comptable dataframe to get categories of account charges
categorie_compte_charges = plan_comptable[
    masque_compte_charges & masque_categorie
].reset_index(drop=True)

# Filter the plan_comptable dataframe to get subcategories of account charges
sous_categorie_compte_charges = plan_comptable[
    masque_compte_charges & masque_sous_categorie
].reset_index(drop=True)

# Extract the first two characters of the "CODE" column to create a new "CLE" column in the sous_categorie_compte_charges DataFrame
sous_categorie_compte_charges["CLE"] = sous_categorie_compte_charges["CODE"].str[:2]

# Merge the categorie_compte_charges and sous_categorie_compte_charges DataFrames on the "CODE" and "CLE" columns, respectively
# The merge is performed as a left join, and the relationship is validated as one-to-many
# The suffixes parameter is used to differentiate between columns with the same name in the two DataFrames
compte_charges = categorie_compte_charges.merge(
    sous_categorie_compte_charges,
    how="left",
    left_on="CODE",
    right_on="CLE",
    validate="one_to_many",
    suffixes=("_CATEGORIE", "_SOUS_CATEGORIE"),
)

# Strip leading and trailing whitespace and capitalize the first letter of each word in the "LIBELLE_CATEGORIE" and "LIBELLE_SOUS_CATEGORIE" columns
for col in ["LIBELLE_CATEGORIE", "LIBELLE_SOUS_CATEGORIE"]:
    compte_charges[col] = compte_charges[col].str.strip().str.capitalize()

# Drop the "CLE" column from the compte_charges DataFrame
compte_charges = compte_charges.drop(columns=["CLE", "CODE_CATEGORIE"], axis=1)

compte_charges.to_parquet(paths.COMPTE_CHARGES_STRUCTURED_FILE_PATH, index=False)
