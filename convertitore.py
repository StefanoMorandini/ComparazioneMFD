import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def prepare_comparison_data(df1, df2):
    # Assuming 'Start Date' is a column in both dataframes, and its format is consistent
    # Merging dataframes on 'Cinema', 'LV', and 'Title' but keeping different 'Start Dates'
    comparison_df = pd.merge(df1, df2, on=['Cinema', 'LV', 'Title'], suffixes=('_df1', '_df2'))
    
    # Ensure that 'Start Date' columns are in datetime format to compare
    comparison_df['Start Date_df1'] = pd.to_datetime(comparison_df['Start Date_df1'])
    comparison_df['Start Date_df2'] = pd.to_datetime(comparison_df['Start Date_df2'])
    
    # Filter to keep rows where 'Start Dates' are different
    comparison_df = comparison_df[comparison_df['Start Date_df1'] != comparison_df['Start Date_df2']]
    
    return comparison_df

def plot_cinema_comparison(comparison_df, cinema_name):
    # Filtering data for the selected cinema
    df_cinema = comparison_df[comparison_df['Cinema'] == cinema_name]
    
    # Selecting columns to compare
    columns_to_compare = ['Adm. Week_df1', 'Adm. Week_df2']  # Example with 'Adm. Week'; extend as needed
    
    # Melt for plotting
    melted_df = pd.melt(df_cinema, id_vars=['Title'], value_vars=columns_to_compare, var_name='Metric', value_name='Value')
    
    # Plotting
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Title', y='Value', hue='Metric', data=melted_df)
    plt.title(f'Comparison for {cinema_name}')
    plt.xticks(rotation=45)
    plt.xlabel('Title')
    plt.ylabel('Value')
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
            
            plot_cinema_comparison(comparison_df, selected_cinema)
        else:
            st.write("No data to display. Please ensure the files have matching 'Cinema', 'LV', 'Title' with different 'Start Dates'.")

if __name__ == "__main__":
    main()

