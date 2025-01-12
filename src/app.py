import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

import constants as csts
import paths
import utils


def main():
    setup_page()

    uploaded_journal_file_path = st.file_uploader("Charger un journal", type=["xlsx"])

    if uploaded_journal_file_path is not None:
        data = process_uploaded_file(uploaded_journal_file_path)

        start_date, end_date = configure_date_filter(data)
        mode_analyse = configure_analysis_mode()
        categories, sub_categories = configure_category_filters(data)

        data = apply_filters(data, start_date, end_date, categories, sub_categories)

        display_metrics(data)
        display_data_table(data, mode_analyse)


def setup_page():
    st.set_page_config(layout="wide")
    st.title(csts.TITLE)
    st.markdown(csts.SUBTITLE)


def process_uploaded_file(uploaded_file_path):
    uploaded_journal = pd.read_excel(
        uploaded_file_path,
        parse_dates=["Date"],
        date_format="%d/%m/%Y",
    )
    journal = utils.process_journal_data(uploaded_journal)
    compte = utils.process_plan_comptable(paths.PLAN_COMPTABLE_RAW_FILE_PATH)
    return utils.process_charges_cube(journal, compte)


def configure_date_filter(data):
    start_date = st.sidebar.date_input(
        label="Sélectionnez une date de début",
        value=data["DATE"].min(),
    )

    end_date = st.sidebar.date_input(
        label="Sélectionnez une date de fin",
        value=data["DATE"].max(),
    )

    return start_date, end_date


def configure_category_filters(data):
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


def configure_analysis_mode():
    return st.sidebar.radio(
        label="Choisir le mode d'analyse 🔐",
        key="visibility",
        options=["Standard", "Groupé"],
    )


def apply_filters(data, start_date, end_date, categories, sub_categories):
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


def display_metrics(data):
    st.metric(
        label="Charges Total (€)",
        value=utils.currency_formating(data["DEBIT"].sum()),
    )


def display_data_table(data, mode_analyse):
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


def configure_grid_columns(gb, mode_analyse):
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
