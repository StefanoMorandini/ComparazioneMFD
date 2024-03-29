import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def prepare_comparison_data(df1, df2):
    comparison_df = pd.merge(df1, df2, on=['Cinema', 'LV', 'Title'], suffixes=('_df1', '_df2'))
    comparison_df['Start Date_df1'] = pd.to_datetime(comparison_df['Start Date_df1'])
    comparison_df['Start Date_df2'] = pd.to_datetime(comparison_df['Start Date_df2'])
    comparison_df = comparison_df[comparison_df['Start Date_df1'] != comparison_df['Start Date_df2']]
    return comparison_df

def plot_cinema_comparison(comparison_df, cinema_name, selected_metric):
    df_cinema = comparison_df[comparison_df['Cinema'] == cinema_name]
    columns_to_compare = [selected_metric + '_df1', selected_metric + '_df2']

    melted_df = pd.melt(df_cinema, id_vars=['Title'], value_vars=columns_to_compare, var_name='Metric', value_name='Value')
    melted_df['Metric'] = melted_df['Metric'].str.replace('_df1', ' (Doc 1)').str.replace('_df2', ' (Doc 2)')
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Title', y='Value', hue='Metric', data=melted_df)
    plt.title(f'Comparison for {cinema_name} - {selected_metric}')
    plt.xticks(rotation=45)
    plt.xlabel('Title')
    plt.ylabel('Value')
    plt.tight_layout()
    
    st.pyplot(plt)

def plot_overview_comparison(comparison_df, cinema_name):
    # Filtra il DataFrame per il cinema selezionato
    df_cinema = comparison_df[comparison_df['Cinema'] == cinema_name]

    # Lista delle colonne di interesse
    columns_to_plot = ['Adm. Wed', 'Adm. Thu', 'Adm. Fri', 'Adm. Sat', 'Adm. Sun', 'Adm. Mon', 'Adm. Tue', 'Adm. Wedn']

    # Melt il DataFrame per adattarlo al plotting
    melted_df = pd.melt(df_cinema, id_vars=['Title'], value_vars=[col + '_df1' for col in columns_to_plot] + [col + '_df2' for col in columns_to_plot],
                        var_name='Day', value_name='Admissions')
    
    # Aggiusta il nome della metrica per il titolo del grafico
    melted_df['Day'] = melted_df['Day'].str.replace('_df1', ' (Doc 1)').str.replace('_df2', ' (Doc 2)')
    
    plt.figure(figsize=(12, 6))
    chart = sns.barplot(x='Day', y='Admissions', hue='Title', data=melted_df)
    plt.title(f'Weekly Admissions Overview for {cinema_name}')
    plt.xticks(rotation=45)
    plt.xlabel('Day of the Week')
    plt.ylabel('Number of Admissions')

    # Aggiungi i valori assoluti sopra ogni barra
    for p in chart.patches:
        chart.annotate(format(p.get_height(), '.1f'), 
                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha = 'center', va = 'center', 
                       xytext = (0, 9), 
                       textcoords = 'offset points')
    
    plt.tight_layout()
    st.pyplot(plt)


def main():
    st.title("Data Comparison Across Cinemas")
    
    file1 = st.file_uploader("Upload first Excel file", type="xlsx", key="file1")
    file2 = st.file_uploader("Upload second Excel file", type="xlsx", key="file2")
    
    if file1 and file2:
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)
        
        comparison_df = prepare_comparison_data(df1, df2)
        
        if not comparison_df.empty:
            cinemas = comparison_df['Cinema'].unique()
            selected_cinema = st.selectbox("Select a Cinema to Compare", options=cinemas)
            
            # Identifica le colonne Adm disponibili per la selezione
            adm_columns = [col for col in comparison_df.columns if 'Adm' in col and ('_df1' in col or '_df2' in col)]
            adm_columns = list(set([col.replace('_df1', '').replace('_df2', '') for col in adm_columns]))
            selected_metric = st.selectbox("Select an Adm Metric to Compare", options=adm_columns)
            
            plot_cinema_comparison(comparison_df, selected_cinema, selected_metric)
        else:
            st.write("No data to display. Please ensure the files have matching 'Cinema', 'LV', 'Title' with different 'Start Dates'.")



if __name__ == "__main__":
    main()
