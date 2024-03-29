import streamlit as st
import pandas as pd

# Funzione per filtrare le colonne di interesse nel DataFrame
def filter_columns(df):
    cols_to_keep = ['Cinema', 'LV'] + [col for col in df.columns if col.startswith('Adm') or col.startswith('L.R.')]
    return df[cols_to_keep]

# Funzione per generare i listati delle colonne che iniziano con 'Adm'
def generate_adm_listings(df):
    adm_columns = [col for col in df.columns if col.startswith('Adm')]
    return [{col: df[col].dropna().unique().tolist()} for col in adm_columns]

# Carica il file tramite Streamlit
uploaded_file = st.file_uploader("Carica il tuo file Excel", type=['xlsx'])

if uploaded_file is not None:
    # Leggi il file Excel
    df = pd.read_excel(uploaded_file)
    
    # Filtra le colonne di interesse
    filtered_df = filter_columns(df)

    # Genera i listati per le colonne 'Adm'
    adm_listings = generate_adm_listings(filtered_df)
    
    # Visualizza il DataFrame filtrato
    st.dataframe(filtered_df)
    
    # Visualizza i listati delle colonne 'Adm'
    for listing in adm_listings:
        st.write(listing)

