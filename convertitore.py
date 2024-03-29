import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Assumi che `comparison_df` sia il tuo DataFrame già preparato
# comparison_df = prepare_comparison_data(df1, df2, columns_to_compare) 

def plot_cinema_comparison(comparison_df, cinema_name, columns_to_compare):
    # Filtra il dataframe per il cinema selezionato
    df_cinema = comparison_df[comparison_df['Cinema'] == cinema_name]
    
    # Prepara i dati per il plotting
    # Assicurati che il DataFrame sia organizzato per permettere un confronto efficace
    melted_df = df_cinema.melt(id_vars=['Cinema', 'LV', 'Title', 'Start Date_df1', 'Start Date_df2'],
                               value_vars=[col + suffix for col in columns_to_compare for suffix in ['_df1', '_df2']],
                               var_name='Metric', value_name='Value')
    
    # Sostituisci i suffissi '_df1' e '_df2' per chiarezza nel grafico
    melted_df['Metric'] = melted_df['Metric'].str.replace('_df1', ' (Doc 1)').str.replace('_df2', ' (Doc 2)')
    
    # Plot
    plt.figure(figsize=(12, 6))
    sns.barplot(data=melted_df, x='Metric', y='Value', hue='Metric')
    plt.title(f'Comparazione per {cinema_name}')
    plt.xticks(rotation=45)
    plt.xlabel('Metrica')
    plt.ylabel('Valore')
    plt.legend(title=cinema_name, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # Mostra il grafico in Streamlit
    st.pyplot(plt)

def main():
    # Caricamento dei dati, esempio con due DataFrame df1 e df2
    
    # Generazione del DataFrame di confronto
    # comparison_df = prepare_comparison_data(df1, df2, columns_to_compare)
    
    # Selezione del cinema
    unique_cinemas = comparison_df['Cinema'].unique()
    selected_cinema = st.selectbox('Seleziona il Cinema:', unique_cinemas)
    
    # Plot per il cinema selezionato
    plot_cinema_comparison(comparison_df, selected_cinema, columns_to_compare)

if __name__ == "__main__":
    main()

