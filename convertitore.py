import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Function to prepare the data for comparison
def prepare_comparison_data(df1, df2, columns_to_compare):
    # Merge the dataframes based on 'Cinema', 'LV', and 'Title'
    comparison_df = pd.merge(df1, df2, on=['Cinema', 'LV', 'Title'], suffixes=('_df1', '_df2'))

    # Filter out rows with the same 'Start Date'
    comparison_df = comparison_df[comparison_df['Start Date_df1'] != comparison_df['Start Date_df2']]

    return comparison_df

# Function to plot the comparison
def plot_comparison(comparison_df, columns_to_compare):
    # Melting the dataframe for easy plotting with seaborn
    comparison_melted = comparison_df.melt(id_vars=['Cinema', 'LV', 'Title'], value_vars=columns_to_compare, 
                                           var_name='Metric', value_name='Value')
    
    # Plotting with seaborn
    plt.figure(figsize=(10, 6))
    sns.barplot(data=comparison_melted, x='Metric', y='Value', hue='Cinema')
    plt.title('Comparison of Metrics between Two Documents')
    plt.xticks(rotation=45)
    plt.legend(title='Cinema')
    plt.tight_layout()
    st.pyplot(plt)

# Main function for Streamlit app
def main():
    st.title("Data Comparison Tool")

    # Uploading the first file
    file1 = st.file_uploader("Upload the first Excel file", type=["xlsx"], key="file1")
    # Uploading the second file
    file2 = st.file_uploader("Upload the second Excel file", type=["xlsx"], key="file2")

    # The columns to compare
    columns_to_compare = ['Adm. Wed', 'Adm. Thu', 'Adm. Fri', 'Adm. Sat', 'Adm. Sun', 'Adm. Weekend',
                          'Adm. Mon', 'Adm. Tue', 'Adm. Wedn', 'Adm. Week', 'Adm. Comp. Week']

    if file1 and file2:
        # Read the data into two separate DataFrames
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)

        # Ensure the columns exist in both DataFrames
        columns_to_compare = [col for col in columns_to_compare if col in df1.columns and col in df2.columns]

        # Prepare the data for comparison
        comparison_df = prepare_comparison_data(df1, df2, columns_to_compare)

        # Display the comparison using a bar chart
        plot_comparison(comparison_df, columns_to_compare)

# Run the main function
if __name__ == "__main__":
    main()
