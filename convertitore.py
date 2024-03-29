import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Definizione delle colonne per il confronto
columns_to_compare = ['Adm. Wed', 'Adm. Thu', 'Adm. Fri', 'Adm. Sat', 'Adm. Sun', 'Adm. Weekend',
                      'Adm. Mon', 'Adm. Tue', 'Adm. Wedn', 'Adm. Week', 'Adm. Comp. Week']

# Funzione per preparare il dataframe per il confronto
def prepare_comparison_data(df1, df2):
    # Filtriamo solo le colonne rilevanti e rimuoviamo le date di fine
    df1_comp = df1[['Cinema', 'Start Date', 'Title', 'LV'] + columns_to_compare]
    df2_comp = df2[['Cinema', 'Start Date', 'Title', 'LV'] + columns_to_compare]
    
    # Uniamo i due dataframe
    merged_df = pd.merge(df1_comp, df2_comp, on=['Cinema', 'Title', 'LV'], suffixes=('_1', '_2'))
    
    # Manteniamo solo le righe con start date differenti
    comparison_df = merged_df[merged_df['Start Date_1'] != merged_df['Start Date_2']]
    
    return comparison_df

# Funzione per visualizzare il confronto in un grafico a barre
def plot_comparison(comparison_df):
    # Fondere le righe per avere una differenziazione chiara nel grafico
    comparison_df = pd.melt(comparison_df, id_vars=['Cinema', 'Title', 'LV'], 
                            value_vars=[col + '_1' for col in columns_to_compare] + [col + '_2' for col in columns_to_compare], 
                            var_name='Measurement', value_name='Value')
    
    # Grafico a barre
    plt.figure(figsize=(10, 6))
    sns.barplot(data=comparison_df, x='Measurement', y='Value', hue='Cinema')
    plt.xticks(rotation=90)
    plt.tight_layout()
    st.pyplot(plt)

# Funzione principale dell'app Streamlit
def main():
    st.title("Confronto Dati di Cinema")

    # Caricamento dei file
    uploaded_file_1 = st.file_uploader("Carica il primo file Excel", type=["xlsx"], key="file1")
    uploaded_file_2 = st.file_uploader("Carica il secondo file Excel", type=["xlsx"], key="file2")
    
    # Verifichiamo se entrambi i file sono stati caricati
    if uploaded_file_1 and uploaded_file_2:
        # Lettura dei dati dai file
        data1 = pd.read_excel(uploaded_file_1)
        data2 = pd.read_excel(uploaded_file_2)
        
        # Prepariamo i dati per il confronto
        comparison_df = prepare_comparison_data(data1, data2)
        
        # Mostra un messaggio se non ci sono righe da confrontare
        if comparison_df.empty:
            st.write("Non ci sono elementi da confrontare con le date di inizio diverse.")
        else:
            # Altrimenti, visualizziamo il confronto
            st.write("Confronto dei dati:")
            plot_comparison(comparison_df)

# Esecuzione della funzione principale
if __name__ == "__main__":
    main()
