import pandas as pd
import streamlit as st


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


@st.cache_data()
def process_journal_data(journal: pd.DataFrame) -> pd.DataFrame:
    """
    Reads, cleans, and processes journal data from an Excel file and saves it as a Parquet file.

    Args:
        input_path (str): Path to the input Excel file.
        output_path (str): Path to the output Parquet file.
    """

    # Clean the column names
    journal.columns = clean_col_names(journal)

    # Convert "DEBIT" and "CREDIT" columns to float
    for col in ["DEBIT", "CREDIT"]:
        journal[col] = journal[col].astype(float)

    # Create a formatted date string column
    journal["DATE_STR"] = pd.to_datetime(
        journal["DATE"], format="%d/%m/%Y"
    ).dt.strftime("%Y-%m-%d")

    return journal


@st.cache_data()
def process_plan_comptable(input_path: str) -> pd.DataFrame:
    """
    Processes the plan comptable data to generate a structured file with categories and subcategories.

    Args:
        input_path (str): Path to the raw plan comptable Excel file.
        output_path (str): Path to save the processed Parquet file.
    """
    # Read the raw plan comptable data
    plan_comptable = pd.read_excel(input_path, dtype=str)

    # Rename the columns
    plan_comptable.columns = ["CODE", "LIBELLE"]

    # Create masks for filtering rows
    masque_compte_charges = (
        plan_comptable["CODE"].str[0] == "6"
    )  # Rows starting with "6"
    masque_categorie = plan_comptable["CODE"].str.len() == 2  # Rows with code length 2
    masque_sous_categorie = (
        plan_comptable["CODE"].str.len() == 3
    )  # Rows with code length 3

    # Filter categories and subcategories
    categorie_compte_charges = plan_comptable[
        masque_compte_charges & masque_categorie
    ].reset_index(drop=True)

    sous_categorie_compte_charges = plan_comptable[
        masque_compte_charges & masque_sous_categorie
    ].reset_index(drop=True)

    # Add a "CLE" column to subcategories
    sous_categorie_compte_charges["CLE"] = sous_categorie_compte_charges["CODE"].str[:2]

    # Merge categories and subcategories
    compte_charges = categorie_compte_charges.merge(
        sous_categorie_compte_charges,
        how="left",
        left_on="CODE",
        right_on="CLE",
        validate="one_to_many",
        suffixes=("_CATEGORIE", "_SOUS_CATEGORIE"),
    )

    # Clean and format the "LIBELLE" columns
    for col in ["LIBELLE_CATEGORIE", "LIBELLE_SOUS_CATEGORIE"]:
        compte_charges[col] = compte_charges[col].str.strip().str.capitalize()

    # Drop unnecessary columns
    compte_charges = compte_charges.drop(columns=["CLE", "CODE_CATEGORIE"], axis=1)

    # Save the processed data to a Parquet file
    return compte_charges


@st.cache_data()
def process_charges_cube(
    journal: pd.DataFrame, compte_charges: pd.DataFrame
) -> pd.DataFrame:
    """
    Processes journal and plan comptable data to generate a structured cube of charges.

    Args:
        journal_path (str): Path to the structured journal Parquet file.
        compte_charges_path (str): Path to the processed plan comptable Parquet file.
        cube_output_path (str): Path to save the processed cube as a Parquet file.
    """

    # Filter journal rows where the "COMPTE" column starts with "6"
    masque_charge = journal["COMPTE"].str[0] == "6"
    charges = journal.loc[masque_charge].reset_index(drop=True)

    # Create a "CLE" column in the charges dataframe
    charges["CLE"] = charges["COMPTE"].str[:3]

    # Merge charges with plan comptable
    charges_plan_de_compte = charges.merge(
        right=compte_charges,
        how="left",
        left_on="CLE",
        right_on="CODE_SOUS_CATEGORIE",
        validate="m:1",
    )

    # Drop unnecessary columns and filter for relevant ones
    charges_plan_de_compte = charges_plan_de_compte.drop(
        columns=[
            "CLE",
            "CODE_SOUS_CATEGORIE",
            "JOURNAL",
            "CREDIT",
            "ECHEANCE",
            "PIECE",
            "REF_PIECE",
            "COMPTE",
        ],
        axis=1,
    ).filter(
        [
            "DATE",
            "LIBELLE_CATEGORIE",
            "LIBELLE_SOUS_CATEGORIE",
            "LIBELLE",
            "DEBIT",
            "DATE_STR",
        ]
    )

    # Save the processed cube to a Parquet file
    return charges_plan_de_compte
