import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

import constants as csts
import paths
from utils import currency_formating

st.set_page_config(layout="wide")
st.title(csts.TITLE)
st.markdown(csts.SUBTITLE)


@st.cache_data()
def load_data():
    data = pd.read_parquet(paths.CUBE_FILE_PATH)
    return data


data = load_data()

# Filtrage par date
start_date = st.sidebar.date_input(
    "Sélectionnez une date de début",
    value=data["DATE"].min(),
)
end_date = st.sidebar.date_input(
    "Sélectionnez une date de fin",
    value=data["DATE"].max(),
)

# should_display_pivoted = st.sidebar.button("Démarrage de l'analyse")

mode_analyse = st.sidebar.radio(
    "Choisir le mode d'analyse 👉",
    key="visibility",
    options=["Standard", "Groupé"],
)

if start_date and end_date:
    data = data[
        (data["DATE"] >= pd.to_datetime(start_date))
        & (data["DATE"] <= pd.to_datetime(end_date))
    ]
    st.write(f"Filtré entre {start_date} et {end_date}")

# Filtrage par catégorie
categories = st.sidebar.multiselect(
    "Filtrer par catégorie",
    options=data["LIBELLE_CATEGORIE"].unique(),
    default=data["LIBELLE_CATEGORIE"].unique(),
)

if categories:
    data = data[data["LIBELLE_CATEGORIE"].isin(categories)]

# Filtrage par sous-catégorie
sub_categories = st.sidebar.multiselect(
    "Filtrer par sous-catégorie",
    options=data["LIBELLE_SOUS_CATEGORIE"].unique(),
    default=data["LIBELLE_SOUS_CATEGORIE"].unique(),
)

if sub_categories:
    data = data[data["LIBELLE_SOUS_CATEGORIE"].isin(sub_categories)]

# Indicateurs
total_cost = st.metric(
    label="Charges Total (€)",
    value=currency_formating(data["DEBIT"].sum()),
)

if mode_analyse == "Standard":
    gb = GridOptionsBuilder()

    gb.configure_default_column(
        resizable=True,
        filterable=True,
        sortable=True,
        editable=False,
    )

    # Configuration des colonnes
    gb.configure_column(
        field="LIBELLE_CATEGORIE",
        header_name="Catégorie",
        width=100,
    )

    gb.configure_column(
        field="LIBELLE_SOUS_CATEGORIE",
        header_name="Sous Catégorie",
        width=250,
    )

    gb.configure_column(
        field="LIBELLE",
        header_name="Libellé",
        width=100,
    )

    gb.configure_column(
        field="DATE_STR",
        header_name="Date",
        width=100,
        valueFormatter=csts.DATE_FORMATTER,
    )

    gb.configure_column(
        field="DEBIT",
        header_name="Charges (€)",
        width=100,
        type=["numericColumn"],
        valueFormatter=csts.CURRENCY_FORMATTER,
    )

    go = gb.build()

    # Affichage du tableau
    AgGrid(
        data,
        gridOptions=go,
        height=600,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=False,
        theme="streamlit",
    )

if mode_analyse == "Groupé":
    # Configuration de la grille AgGrid
    gb = GridOptionsBuilder()

    gb.configure_default_column(
        resizable=True,
        filterable=True,
        sortable=True,
        editable=False,
    )

    # Configuration des colonnes
    gb.configure_column(
        field="LIBELLE_CATEGORIE",
        header_name="Catégorie",
        width=100,
        rowGroup=True,
    )

    gb.configure_column(
        field="LIBELLE_SOUS_CATEGORIE",
        header_name="Sous Catégorie",
        width=250,
        rowGroup=True,
    )

    gb.configure_column(
        field="LIBELLE",
        header_name="Libellé",
        width=100,
        rowGroup=True,
    )

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
        # pivotMode=should_display_pivoted,
        pivotMode=True,
        domLayout="normal",
    )

    go = gb.build()

    # Affichage du tableau
    AgGrid(
        data,
        gridOptions=go,
        height=600,
        fit_columns_on_grid_load=True,
        theme="streamlit",
    )
