import locale

import pandas as pd
import plotly.express as px

# import plotly.graph_objects as go
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

import constants as csts
import utils

# Set locale to French
locale.setlocale(locale.LC_TIME, "fr_FR.utf8")


def main() -> None:
    """Main function to set up and run the Streamlit application."""
    setup_page()

    uploaded_journal_file_path = st.file_uploader(
        label="Charger le journal", type=["xlsx"], accept_multiple_files=True
    )
    uploaded_compte_file_path = st.file_uploader(
        label="Charger le fichier de compte", type=["xlsx"], accept_multiple_files=False
    )

    if uploaded_journal_file_path and uploaded_compte_file_path is not None:
        data = process_uploaded_file(
            uploaded_journal_file_path, uploaded_compte_file_path
        )
        start_date, end_date = configure_date_filter(data)
        mode_analyse = configure_analysis_mode()
        categories, sub_categories = configure_category_filters(data)
        data = apply_filters(data, start_date, end_date, categories, sub_categories)
        display_metrics(data)
        if mode_analyse == "Standard":
            display_graph(data)
        display_data_table(data, mode_analyse)


def setup_page() -> None:
    """Set up the Streamlit page configuration and display the title and subtitle."""
    st.set_page_config(layout="wide")
    st.title(csts.TITLE)
    st.markdown(csts.SUBTITLE)


def process_uploaded_file(
    uploaded_file_path: str, uploaded_compte_file_path: str
) -> pd.DataFrame:
    """Process the uploaded journal file and return a processed DataFrame.

    Args:
        uploaded_file_path (str): Path to the uploaded Excel file.

    Returns:
        pd.DataFrame: Processed journal data.
    """

    uploaded_journal_to_concat = []

    # Pour chaque journal, on lit le fichier et on l'ajoute à la liste
    for journal_file_path in uploaded_file_path:
        uploaded_journal = pd.read_excel(
            journal_file_path,
            parse_dates=["Date"],
            date_format="%d/%m/%Y",
        )

        uploaded_journal_to_concat.append(uploaded_journal)

    # On concatène tous les journaux en un seul DataFrame
    uploaded_journal_concat = pd.concat(
        objs=uploaded_journal_to_concat, ignore_index=True
    )
    uploaded_compte = pd.read_excel(uploaded_compte_file_path, dtype=str)

    journal = utils.process_journal_data(uploaded_journal_concat)
    compte = utils.process_plan_comptable(uploaded_compte)
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

        start_date_formatted = start_date.strftime("%d %B %Y")
        end_date_formatted = end_date.strftime("%d %B %Y")

        st.write(f"Filtré entre le {start_date_formatted} et le {end_date_formatted}")

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

    col1, col2, col3, col4 = st.columns(4)
    col5, col6, col7, col8 = st.columns(4)

    charges_total = data["DEBIT"].sum()
    achats = data.loc[data["LIBELLE_CATEGORIE"] == "Achats (sauf 603)", "DEBIT"].sum()
    personnel = data.loc[
        data["LIBELLE_CATEGORIE"] == "Charges de personnel", "DEBIT"
    ].sum()
    services_ext = data.loc[
        data["LIBELLE_CATEGORIE"] == "Services extérieurs", "DEBIT"
    ].sum()
    autres_charges = data.loc[
        data["LIBELLE_CATEGORIE"] == "Autres charges de gestion courante", "DEBIT"
    ].sum()
    impots_charges = data.loc[
        data["LIBELLE_CATEGORIE"] == "Impôts, taxes et versements assimilés", "DEBIT"
    ].sum()
    charges_excep = data.loc[
        data["LIBELLE_CATEGORIE"] == "Charges exceptionnelles", "DEBIT"
    ].sum()
    autres_services_ext = data.loc[
        data["LIBELLE_CATEGORIE"] == "Autres services extérieurs", "DEBIT"
    ].sum()

    with col1:
        st.metric(
            label="Charges Total (€)",
            value=f"{utils.currency_formating(charges_total)}",
            border=True,
        )
    with col2:
        st.metric(
            label="Achats (sauf 603)",
            value=f"{utils.currency_formating(achats)}",
            border=True,
        )
    with col3:
        st.metric(
            label="Charges de personnel",
            value=f"{utils.currency_formating(personnel)}",
            border=True,
        )

    with col4:
        st.metric(
            label="Services extérieurs",
            value=f"{utils.currency_formating(services_ext)}",
            border=True,
        )
    with col5:
        st.metric(
            label="Autres services extérieurs",
            value=f"{utils.currency_formating(autres_services_ext)}",
            border=True,
        )
    with col6:
        st.metric(
            label="Impôts, taxes et versements assimilés",
            value=f"{utils.currency_formating(impots_charges)}",
            border=True,
        )

    with col7:
        st.metric(
            label="Charges exceptionnelles",
            value=f"{utils.currency_formating(charges_excep)}",
            border=True,
        )
    with col8:
        st.metric(
            label="Autres charges de gestion courante",
            value=f"{utils.currency_formating(autres_charges)}",
            border=True,
        )


def display_graph(data: pd.DataFrame) -> None:
    """Display a pie chart showing the total charges per category with enhanced aesthetics.

    Args:
        data (pd.DataFrame): DataFrame containing the data.
    """
    # Préparer les données
    grouped_data = data.groupby("LIBELLE_CATEGORIE")["DEBIT"].sum().reset_index()

    # Créer le graphique en camembert
    fig = px.pie(
        grouped_data,
        values="DEBIT",
        names="LIBELLE_CATEGORIE",
        title="Répartition des charges par Catégorie",
        labels={"DEBIT": "Charges (€)"},
    )

    # Personnaliser les tracés
    fig.update_traces(
        textposition="inside",
        text=grouped_data["DEBIT"].map(
            lambda x: f"{x:,.0f} €".replace(",", " ").replace(".", ",")
        ),
        textinfo="percent+text",
    )

    # Configurer la mise en page pour agrandir le graphique
    fig.update_layout(
        uniformtext_minsize=20,
        uniformtext_mode="hide",
        width=1000,  # Largeur du graphique
        height=700,  # Hauteur du graphique
        title_font_size=24,
        title_x=0.5,  # Centrer le titre
        legend_title_text="Catégorie",
        legend=dict(
            font=dict(size=16),  # Taille de la police de la légende
            # orientation="h",
            # yanchor="top",
            # y=-0.2,  # Ajuste la position sous le graphique
            # xanchor="center",
            # x=0.5,
        ),
    )

    # Afficher le graphique avec Streamlit
    st.plotly_chart(
        fig, use_container_width=False
    )  # Désactiver l'auto-ajustement pour conserver les dimensions


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
