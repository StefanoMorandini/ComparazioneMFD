import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def prepare_comparison_data(df1, df2):
    # Merging dataframes on 'Cinema', 'LV', and 'Title' but keeping different 'Start Dates'
    comparison_df = pd.merge(df1, df2, on=['Cinema', 'LV', 'Title'], suffixes=('_df1', '_df2'))
    # Ensure that 'Start Date' columns are in datetime format to compare
    comparison_df['Start Date_df1'] = pd.to_datetime(comparison_df['Start Date_df1'])
    comparison_df['Start Date_df2'] = pd.to_datetime(comparison_df['Start Date_df2'])
    # Filter to keep rows where 'Start Dates' are different
    comparison_df = comparison_df[comparison_df['Start Date_df1'] != comparison_df['Start Date_df2']]
    return comparison_df

def plot_overview_comparison(comparison_df, cinema_name):
    df_cinema = comparison_df[comparison_df['Cinema'] == cinema_name]
    columns_to_plot = ['Adm. Wed', 'Adm. Thu', 'Adm. Fri', 'Adm. Sat', 'Adm. Sun', 'Adm. Mon', 'Adm. Tue', 'Adm. Wedn']
    melted_df = pd.melt(df_cinema, id_vars=['Title'], value_vars=[col + '_df1' for col in columns_to_plot] + [col + '_df2' for col in columns_to_plot],
                        var_name='Day', value_name='Admissions')
    melted_df['Day'] = melted_df['Day'].str.replace('_df1', ' (Doc 1)').str.replace('_df2', ' (Doc 2)')
    
    plt.figure(figsize=(14, 7))
    chart = sns.barplot(x='Day', y='Admissions', hue='Title', data=melted_df)
    plt.title(f'Weekly Admissions Overview for {cinema_name}')
    plt.xticks(rotation=45)
    plt.xlabel('Day of the Week')
    plt.ylabel('Number of Admissions')

    # Add absolute values above each bar
    for p in chart.patches:
        chart.annotate(f'{int(p.get_height())}', 
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
            
            plot_overview_comparison(comparison_df, selected_cinema)
        else:
            st.write("No data to display. Please ensure the files have matching 'Cinema', 'LV', 'Title' with different 'Start Dates'.")

if __name__ == "__main__":
    main()
