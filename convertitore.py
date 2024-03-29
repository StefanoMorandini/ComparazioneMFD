import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def prepare_comparison_data(df1, df2):
    # Definizione delle colonne per il confronto
    columns_to_compare = ['Adm. Wed', 'Adm. Thu', 'Adm. Fri', 'Adm. Sat', 'Adm. Sun', 'Adm. Weekend',
                          'Adm. Mon', 'Adm. Tue', 'Adm. Wedn', 'Adm. Week', 'Adm. Comp. Week']
    # Unione dei dataframe su 'Cinema', 'LV', e 'Title', mantenendo distinte le 'Start Date'
    comparison_df = pd.merge(df1, df2, on=['Cinema', 'LV', 'Title'], suffixes=('_df1', '_df2'))
    # Filtro per mantenere solo le righe con 'Start Date' diverse
    comparison_df = comparison_df[comparison_df['Start Date_df1'] != comparison_df['Start Date_df2']]
    return comparison_df

def plot_cinema_comparison(comparison_df, cinema_name):
    # Filtraggio per il cinema selezionato
    df_cinema = comparison_df[comparison_df['Cinema'] == cinema_name]
    
    # Preparazione dei dati per la visualizzazione
    columns_to_melt = [col + suffix for col in columns_to_compare for suffix in ['_df1', '_df2']]
    melted_df = df_cinema.melt(id_vars=['Title'], value_vars=columns_to_melt, var_name='Metric', value_name='Value')
    
    # Aggiustamento delle etichette per chiarezza nel grafico
    melted_df['Metric'] = melted_df['Metric'].str.replace('_df1', ' (Doc 1)').str.replace('_df2', ' (Doc 2)')
    
    # Creazione del grafico
    plt.figure(figsize=(14, 8))
    sns.barplot(x='Metric', y='Value', hue='Title', data=melted_df)
    plt.title(f'Comparazione per {cinema_name}')
    plt.xticks(rotation=45)
    plt.xlabel('Metrica')
    plt.ylabel('Valore')
    plt.legend(title='Titolo', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # Mostra il grafico in Streamlit
    st.pyplot(plt)

def main():
    st.title("Comparazione dei Dati tra Cinemas")
    
    file1 = st.file_uploader("Carica il primo file Excel", type="xlsx", key="file1")
    file2 = st.file_uploader("Carica il secondo file Excel", type="xlsx", key="file2")
    
    if file1 and file2:
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)
        
        comparison_df = prepare_comparison_data(df1, df2)
        
        if not comparison_df.empty:
            cinemas = comparison_df['Cinema'].unique()
            selected_cinema = st.selectbox("Seleziona un Cinema per la comparazione", options=cinemas)
            
            plot_cinema_comparison(comparison_df, selected_cinema)
        else:
            st.write("Nessun dato disponibile per la visualizzazione. Assicurati che i file contengano 'Cinema', 'LV', 'Title' con 'Start Dates' differenti.")

if __name__ == "__main__":
    main()

