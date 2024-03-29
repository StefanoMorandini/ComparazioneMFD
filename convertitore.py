import streamlit as st
import pandas as pd

# Carica il file tramite Streamlit
uploaded_file = st.file_uploader("Carica il tuo file Excel", type=['xlsx'])

if uploaded_file is not None:
    # Leggi il file Excel
    df = pd.read_excel(uploaded_file)
    
    # Identifica le colonne 'Adm' e include 'Cinema', 'LV', 'Start date'
    cols_to_keep = ['Cinema', 'LV', 'Start date'] + [col for col in df.columns if col.startswith('Adm')]
    filtered_df = df[cols_to_keep]

    # Raggruppa per 'Cinema', 'LV', 'Start date' e aggrega i valori delle colonne 'Adm'
    group_cols = ['Cinema', 'LV', 'Start date']
    adm_columns = [col for col in filtered_df.columns if col.startswith('Adm')]
    
    # Aggrega i dati in liste (o altra forma desiderata) per ogni colonna 'Adm' all'interno di ogni gruppo
    aggregated_df = filtered_df.groupby(group_cols)[adm_columns].agg(lambda x: list(x.dropna().unique())).reset_index()

    # Visualizza il nuovo DataFrame aggregato
    st.dataframe(aggregated_df)
    
