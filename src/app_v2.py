import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")
st.title("Analyse financière PEE Freitas 🏆")


@st.cache_data()
def load_data():
    data = pd.read_excel(io="/app/workspace/exemple.xlsx", parse_dates=["DATE"])
    return data


data = load_data()

start_date = st.date_input("Sélectionnez une date de début", value=data["DATE"].min())
end_date = st.date_input("Sélectionnez une date de fin", value=data["DATE"].max())
should_display_pivoted = st.checkbox("Démarrage de l'analyse")

# Filtrer les données
if start_date and end_date:
    data = data[
        (data["DATE"] >= pd.to_datetime(start_date))
        & (data["DATE"] <= pd.to_datetime(end_date))
    ]
    st.write(f"Filtré entre {start_date} et {end_date}")

# Ajoutez le CSS pour styliser les en-têtes directement dans Streamlit

gb = GridOptionsBuilder()

# Exemple d'ajout de styles pour les cellules
gb.configure_default_column(
    resizable=True,
    filterable=True,
    sortable=True,
    editable=False,
    # cellStyle={
    #     "font-size": "20px"
    # },  # Augmente la taille de la police pour les cellules
)

gb.configure_column(
    field="CATEGORIE",
    header_name="Catégorie",
    width=100,
    rowGroup=should_display_pivoted,
)

gb.configure_column(
    field="DEFINITION",
    header_name="Définition",
    width=250,
    rowGroup=should_display_pivoted,
)

gb.configure_column(
    field="LIBELLE",
    header_name="Libellé",
    width=100,
    rowGroup=should_display_pivoted,
)

gb.configure_column(
    field="DATE",
    header_name="Date",
    width=100,
    valueFormatter="value != undefined ? new Date(value).toLocaleString('fr-FR', {dateStyle:'medium'}): ''",
    pivot=False,
)

gb.configure_column(
    field="virtualYear",
    header_name="Année",
    width=100,
    valueGetter="new Date(data.DATE).getFullYear()",
    pivot=True,
    hide=True,
)

gb.configure_column(
    field="virtualMonth",
    header_name="Mois",
    width=100,
    valueGetter="new Date(data.DATE).toLocaleDateString('en-US',options={year:'numeric', month:'2-digit'})",
    pivot=True,
    hide=True,
)

gb.configure_column(
    field="DEBIT",
    header_name="Charges (€)",
    width=100,
    type=["numericColumn"],
    aggFunc="sum",
    valueFormatter="x.toLocaleString('fr-FR', {style: 'currency', currency: 'EUR'})",
)

gb.configure_grid_options(
    tooltipShowDelay=0,
    pivotMode=should_display_pivoted,
    domLayout="normal",  # Ajuste la largeur du tableau à l'écran
)

go = gb.build()

AgGrid(
    data,
    gridOptions=go,
    height=600,
    fit_columns_on_grid_load=True,  # Affichage du tableau en pleine largeur
    theme="streamlit",  # Utilisation du thème par défaut Streamlit
)
