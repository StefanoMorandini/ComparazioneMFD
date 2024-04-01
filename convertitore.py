import streamlit as st
import pandas as pd
from datetime import timedelta

def rename_columns_based_on_input_date(df, input_date):
    original_columns = ['Adm. Wed', 'Amd. Thu', 'Adm. Fri', 'Adm. Sat', 'Adm. Sun', 'Adm. Mon', 'Adm. Tue']
    rename_dict = {}
    for i, col in enumerate(original_columns):
        new_name = (input_date + timedelta(days=i)).strftime('%Y-%m-%d')
        if col in df.columns:
            rename_dict[col] = new_name
    return df.rename(columns=rename_dict), list(rename_dict.values())

def add_total_row(df):
    total_row = df.sum(numeric_only=True)
    total_row.name = 'Total'
    df = pd.concat([df, pd.DataFrame(total_row).transpose()])
    return df

def process_file(file, input_date):
    df = pd.read_excel(file)
    columns_to_drop = ['Dim', 'Box. Weekend', 'Box. Week', 'Start Date', 'End Date', 'TT', 'Distr.', 'Dim.', 'MT', 'Adm. Week', 'Adm. Weekend', 'Adm. Comp. Week', 'Adm. Wedn']
    df = df.drop(columns=[col for col in df.columns if col in columns_to_drop or 'Box' in col], errors='ignore')
    
    df, new_column_names = rename_columns_based_on_input_date(df, input_date)
    df = add_total_row(df)
    
    if 'Cinema' in df.columns:
        df.set_index('Cinema', inplace=True)
    else:
        st.error("'Cinema' column not found in the DataFrame. Please check your file.")
        return pd.DataFrame()
    
    return df

def compare_dataframes(df1, df2):
    # Filter numeric columns for comparison
    numeric_cols_df1 = df1.select_dtypes(include=['number']).columns
    numeric_cols_df2 = df2.select_dtypes(include=['number']).columns
    common_numeric_cols = set(numeric_cols_df1).intersection(set(numeric_cols_df2))
    
    # Initialize comparison DataFrame
    comparison_df = pd.DataFrame(index=df1.index)
    
    # Perform comparison for common numeric columns
    for col in common_numeric_cols:
        comparison_df[col] = df1[col] - df2[col]
    
    return comparison_df

# Streamlit UI
st.title('Cinema Data Processor with Date Selection and Comparison')

input_date = st.date_input("Select the start date for renaming 'Adm' columns:", value=pd.to_datetime('today'))
uploaded_file1 = st.file_uploader("Choose the first Excel file", type=['xlsx'], key='file1')
uploaded_file2 = st.file_uploader("Choose the second Excel file", type=['xlsx'], key='file2')

if uploaded_file1 and uploaded_file2 and input_date:
    processed_data1 = process_file(uploaded_file1, input_date)
    processed_data2 = process_file(uploaded_file2, input_date)
    
    if not processed_data1.empty and not processed_data2.empty:
        comparison_df = compare_dataframes(processed_data1, processed_data2)
        st.write("Comparison Results", comparison_df)
        
        csv_comparison = comparison_df.to_csv().encode('utf-8')
        st.download_button("Download comparison data as CSV", data=csv_comparison, file_name='comparison_data.csv', mime='text/csv')
    else:
        st.error("Processing failed or resulted in an empty DataFrame for one or both files.")


