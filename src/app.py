import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

import constants as csts
import paths
import utils


def main() -> None:
    """Main function to set up and run the Streamlit application."""
    setup_page()

    uploaded_journal_file_path = st.file_uploader("Charger un journal", type=["xlsx"])

    if uploaded_journal_file_path is not None:
        data = process_uploaded_file(uploaded_journal_file_path)

        start_date, end_date = configure_date_filter(data)
        categories, sub_categories = configure_category_filters(data)
        mode_analyse = configure_analysis_mode()

        data = apply_filters(data, start_date, end_date, categories, sub_categories)

        display_metrics(data)
        display_data_table(data, mode_analyse)


def setup_page() -> None:
    """Set up the Streamlit page configuration and display the title and subtitle."""
    st.set_page_config(layout="wide")
    st.title(csts.TITLE)
    st.markdown(csts.SUBTITLE)


def process_uploaded_file(uploaded_file_path: str) -> pd.DataFrame:
    """Process the uploaded journal file and return a processed DataFrame.

    Args:
        uploaded_file_path (str): Path to the uploaded Excel file.

    Returns:
        pd.DataFrame: Processed journal data.
    """
    uploaded_journal = pd.read_excel(
        uploaded_file_path,
        parse_dates=["Date"],
        date_format="%d/%m/%Y",
    )
    journal = utils.process_journal_data(uploaded_journal)
    compte = utils.process_plan_comptable(paths.PLAN_COMPTABLE_RAW_FILE_PATH)
    return utils.process_charges_cube(journal, compte)


def configure_date_filter(data: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Configure and return the date filter values.

    Args:
        data (pd.DataFrame): DataFrame containing the data to filter.

    Returns:
        tuple[pd.Timestamp, pd.Timestamp]: Start and end dates for the filter.
    """
    start_date = st.sidebar.date_input(
        label="Sélectionnez une date de début",
        value=data["DATE"].min(),
    )

    end_date = st.sidebar.date_input(
        label="Sélectionnez une date de fin",
        value=data["DATE"].max(),
    )

    return start_date, end_date


def configure_category_filters(data: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Configure and return the category and sub-category filter values.

    Args:
        data (pd.DataFrame): DataFrame containing the data to filter.

    Returns:
        tuple[list[str], list[str]]: Selected categories and sub-categories.
    """
    categories = st.sidebar.multiselect(
        label="Filtrer par catégorie",
        options=data["LIBELLE_CATEGORIE"].unique(),
        default=data["LIBELLE_CATEGORIE"].unique(),
    )

    sub_categories = st.sidebar.multiselect(
        label="Filtrer par sous-catégorie",
        options=data["LIBELLE_SOUS_CATEGORIE"].unique(),
        default=data["LIBELLE_SOUS_CATEGORIE"].unique(),
    )

    return categories, sub_categories


def configure_analysis_mode() -> str:
    """Configure and return the selected analysis mode.

    Returns:
        str: Selected analysis mode ("Standard" or "Groupé").
    """
    return st.sidebar.radio(
        label="Choisir le mode d'analyse 🔐",
        key="visibility",
        options=["Standard", "Groupé"],
    )


def apply_filters(
    data: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    categories: list[str],
    sub_categories: list[str],
) -> pd.DataFrame:
    """Apply filters to the data and return the filtered DataFrame.

    Args:
        data (pd.DataFrame): DataFrame to filter.
        start_date (pd.Timestamp): Start date for filtering.
        end_date (pd.Timestamp): End date for filtering.
        categories (list[str]): List of selected categories.
        sub_categories (list[str]): List of selected sub-categories.

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    if start_date and end_date:
        data = data[
            data["DATE"].between(pd.to_datetime(start_date), pd.to_datetime(end_date))
        ]
        st.write(f"Filtré entre {start_date} et {end_date}")

    if categories:
        data = data[data["LIBELLE_CATEGORIE"].isin(categories)]

    if sub_categories:
        data = data[data["LIBELLE_SOUS_CATEGORIE"].isin(sub_categories)]

    return data


def display_metrics(data: pd.DataFrame) -> None:
    """Display metrics like total charges.

    Args:
        data (pd.DataFrame): DataFrame containing the data.
    """
    st.metric(
        label="Charges Total (€)",
        value=utils.currency_formating(data["DEBIT"].sum()),
    )


def display_data_table(data: pd.DataFrame, mode_analyse: str) -> None:
    """Display the data table using AgGrid with appropriate configurations.

    Args:
        data (pd.DataFrame): DataFrame containing the data to display.
        mode_analyse (str): Selected analysis mode ("Standard" or "Groupé").
    """
    gb = GridOptionsBuilder()
    configure_grid_columns(gb, mode_analyse)
    go = gb.build()

    AgGrid(
        data,
        gridOptions=go,
        height=600,
        fit_columns_on_grid_load=True,
        theme="streamlit",
    )


def configure_grid_columns(gb: GridOptionsBuilder, mode_analyse: str) -> None:
    """Configure the grid columns based on the selected analysis mode.

    Args:
        gb (GridOptionsBuilder): Grid options builder instance.
        mode_analyse (str): Selected analysis mode ("Standard" or "Groupé").
    """
    gb.configure_default_column(
        resizable=True,
        filterable=True,
        sortable=True,
        editable=False,
    )

    gb.configure_column(
        field="LIBELLE_CATEGORIE",
        header_name="Catégorie",
        width=100,
        rowGroup=True if mode_analyse == "Groupé" else False,
    )

    gb.configure_column(
        field="LIBELLE_SOUS_CATEGORIE",
        header_name="Sous Catégorie",
        width=250,
        rowGroup=True if mode_analyse == "Groupé" else False,
    )

    gb.configure_column(
        field="LIBELLE",
        header_name="Libellé",
        width=100,
        rowGroup=True if mode_analyse == "Groupé" else False,
    )

    gb.configure_column(
        field="DEBIT",
        header_name="Charges (€)",
        width=100,
        type=["numericColumn"],
        valueFormatter=csts.CURRENCY_FORMATTER,
    )

    if mode_analyse == "Standard":
        gb.configure_column(
            field="DATE",
            header_name="Date",
            width=100,
            valueFormatter=csts.DATE_FORMATTER,
        )

    if mode_analyse == "Groupé":
        gb.configure_column(
            field="DATE",
            header_name="Date",
            width=100,
            valueFormatter=csts.DATE_FORMATTER,
            pivot=False,
        )
        gb.configure_column(
            field="virtualYear",
            header_name="Année",
            width=100,
            valueGetter=csts.YEAR_GETTER,
            pivot=True,
            hide=True,
        )
        gb.configure_column(
            field="virtualMonth",
            header_name="Mois",
            width=100,
            valueGetter=csts.MONTH_GETTER,
            pivot=True,
            hide=True,
        )
        gb.configure_column(
            field="DEBIT",
            header_name="Charges (€)",
            width=100,
            type=["numericColumn"],
            aggFunc="sum",
            valueFormatter=csts.CURRENCY_FORMATTER,
        )
        gb.configure_grid_options(
            tooltipShowDelay=0,
            pivotMode=True,
            domLayout="normal",
        )


if __name__ == "__main__":
    main()
