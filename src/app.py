import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

# Étape 1 : Charger un fichier Excel
st.title("PEE Freitas 🏆")
uploaded_file = st.file_uploader("Charger un fichier Excel", type="xlsx")
if uploaded_file:
    if "df" not in st.session_state:
        st.session_state.df = pd.read_excel(uploaded_file)
    df = st.session_state.df
    st.success("Fichier Excel chargé avec succès.")
else:
    st.stop()

# Étape 2 : Génération d'un tableau croisé dynamique
st.header("1. Sélection des critères")
if "pivot_table" not in st.session_state:
    st.session_state.pivot_table = None

with st.form("pivot_form"):
    rows = st.multiselect(
        "Choisir les lignes",
        options=["CATEGORIE"],
        key="rows",
        default=["CATEGORIE"],
    )
    cols = st.multiselect("Choisir les colonnes", options=["AAAAMM"], key="cols")

    submit = st.form_submit_button("Générer")

if submit and rows:
    st.session_state.pivot_table = pd.pivot_table(
        df,
        values="DEBIT",
        index=rows,
        columns=cols if cols else None,
        aggfunc="sum",
    ).reset_index()

if st.session_state.pivot_table is not None:
    pivot_table = st.session_state.pivot_table

    # Convertir les colonnes en chaînes pour éviter les erreurs
    pivot_table.columns = pivot_table.columns.map(str)

    st.header("2. Analyse générale")
    gb = GridOptionsBuilder.from_dataframe(pivot_table)
    gb.configure_selection("single")  # Permet de sélectionner une seule cellule
    gb.configure_column(
        field="DEBIT",
        type=["numericColumn"],
        valueFormatter="x.toLocaleString('fr-FR', {style: 'currency', currency: 'EUR'})",
    )
    grid_options = gb.build()

    grid_response = AgGrid(
        pivot_table,
        gridOptions=grid_options,
        enable_enterprise_modules=False,
        theme="streamlit",  # Options : streamlit, light, dark, etc.
        height=400,
        update_mode="MODEL_CHANGED",
        fit_columns_on_grid_load=True,
    )

    # Étape 3 : Détails associés
    selected = grid_response.get("selected_rows", [])  # .reset_index(drop=True)

    # st.write("DEBUG - rows : ", rows)
    # st.write("DEBUG - rows[0] : ", rows[0])
    # st.write("DEBUG - cols : ", cols)

    if selected is None:
        st.header("3. Détail des charges")
        st.write(
            "Veuillez sélectionner une catégorie dans l'analyse générale pour accéder au détail des charges."
        )

    elif len(selected) > 0:  # Si au moins une cellule est sélectionnée
        st.header("Détail des charges")

        row_var = rows[0]
        selected_value = selected.loc[:, row_var].values[0]
        # st.write("DEBUG - test : ", test)
        cols_of_interest = ["CATEGORIE", "DEFINITION", "DATE", "LIBELLE", "DEBIT"]

        if selected_value:
            detail_df = df.copy()
            mask = detail_df[row_var] == selected_value
            filter_detail_df = detail_df.loc[mask, cols_of_interest].reset_index(
                drop=True
            )
            st.dataframe(
                filter_detail_df.style.format({"DEBIT": "{:,.2f} €"}),
                use_container_width=True,
                height=400,
            )
        else:
            st.write("Aucune cellule sélectionnée.")
