import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def prepare_comparison_data(df1, df2):
    # Assuming 'Start Date' is a column in both dataframes, and its format is consistent
    comparison_df = pd.merge(df1, df2, on=['Cinema', 'LV', 'Title'], suffixes=('_df1', '_df2'))
    # Filter to keep rows where 'Start Dates' are different
    comparison_df = comparison_df[comparison_df['Start Date_df1'] != comparison_df['Start Date_df2']]
    return comparison_df

def plot_cinema_comparison(comparison_df, cinema_name, columns_to_compare):
    df_cinema = comparison_df[comparison_df['Cinema'] == cinema_name]
    
    # Adjust here to include columns_to_compare in the scope
    columns_to_melt = [col + suffix for col in columns_to_compare for suffix in ['_df1', '_df2']]
    melted_df = df_cinema.melt(id_vars=['Title'], value_vars=columns_to_melt, var_name='Metric', value_name='Value')
    
    melted_df['Metric'] = melted_df['Metric'].str.replace('_df1', ' (Doc 1)').str.replace('_df2', ' (Doc 2)')
    
    plt.figure(figsize=(14, 8))
    sns.barplot(x='Metric', y='Value', hue='Title', data=melted_df)
    plt.title(f'Comparison for {cinema_name}')
    plt.xticks(rotation=45)
    plt.xlabel('Metric')
    plt.ylabel('Value')
    plt.legend(title='Title', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    st.pyplot(plt)

def main():
    st.title("Data Comparison Across Cinemas")
    
    file1 = st.file_uploader("Upload first Excel file", type="xlsx", key="file1")
    file2 = st.file_uploader("Upload second Excel file", type="xlsx", key="file2")
    
    if file1 and file2:
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)
        
        columns_to_compare = ['Adm. Wed', 'Adm. Thu', 'Adm. Fri', 'Adm. Sat', 'Adm. Sun', 'Adm. Weekend',
                              'Adm. Mon', 'Adm. Tue', 'Adm. Wedn', 'Adm. Week', 'Adm. Comp. Week']
        
        comparison_df = prepare_comparison_data(df1, df2)
        
        if not comparison_df.empty:
            cinemas = comparison_df['Cinema'].unique()
            selected_cinema = st.selectbox("Select a Cinema to Compare", options=cinemas)
            
            # Pass columns_to_compare to ensure it's accessible
            plot_cinema_comparison(comparison_df, selected_cinema, columns_to_compare)
        else:
            st.write("No data to display. Please ensure the files have matching 'Cinema', 'LV', 'Title' with different 'Start Dates'.")

if __name__ == "__main__":
    main()
