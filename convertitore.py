import streamlit as st
import pandas as pd
from datetime import timedelta

def rename_columns_based_on_input_date(df, input_date):
    original_columns = ['Adm. Wed', 'Amd. Thu', 'Adm. Fri', 'Adm. Sat', 'Adm. Sun', 'Adm. Mon', 'Adm. Tue']
    rename_dict = {}
    for i, col in enumerate(original_columns):
        new_name = (input_date + timedelta(days=i)).strftime('%Y-%m-%d')
        rename_dict[col] = new_name
    return df.rename(columns=rename_dict)

def process_file(file, input_date):
    df = pd.read_excel(file)
    columns_to_drop = ['Dim', 'Box. Weekend', 'Box. Week', 'Start Date', 'End Date', 'TT', 'Distr.', 'Dim.', 'MT', 'Adm. Week', 'Adm. Weekend', 'Adm. Comp. Week', 'Adm. Wedn']
    df = df.drop(columns=[col for col in df.columns if col in columns_to_drop or 'Box' in col], errors='ignore')
    df = rename_columns_based_on_input_date(df, input_date)
    df['Sum of Renamed Columns'] = df.select_dtypes(include=['number']).sum(axis=1)
    df.loc['Total'] = df.select_dtypes(include=['number']).sum()
    if 'Cinema' in df.columns:
        df.set_index('Cinema', inplace=True)
    else:
        df.index.name = 'Cinema'
    return df

def compare_numeric_columns(df1, df2):
    # Ensure no duplicates in the index ('Cinema')
    df1 = df1[~df1.index.duplicated(keep='first')]
    df2 = df2[~df2.index.duplicated(keep='first')]
    
    # Align the DataFrames on the 'Cinema' index
    df1, df2 = df1.align(df2, join='inner', axis=0)
    
    comparison_results = pd.DataFrame(index=df1.index)
    for col in df1.select_dtypes(include=['number']).columns.intersection(df2.select_dtypes(include=['number']).columns):
        comparison_results[f'{col}_diff'] = df1[col] - df2[col]



def init_comparison_df():
    # Initializes or resets the comparison DataFrame.
    return pd.DataFrame()

# Initialize the comparison DataFrame at the start.
comparison_df = init_comparison_df()

st.title('Cinema Data Processor with Date Selection')

input_date1 = st.date_input("Select the start date for renaming 'Adm' columns for the first file:", value=pd.to_datetime('today'), key='date1')
uploaded_file1 = st.file_uploader("Choose the first Excel file", type=['xlsx'], key='file1')

input_date2 = st.date_input("Select the start date for renaming 'Adm' columns for the second file:", value=pd.to_datetime('today'), key='date2')
uploaded_file2 = st.file_uploader("Choose the second Excel file", type=['xlsx'], key='file2')

# Ensure comparison_df is reset or re-initialized to an empty DataFrame here if needed.

processed_data1, processed_data2 = None, None  # Explicitly define these variables to avoid reference before assignment.

if uploaded_file1 and uploaded_file2 and input_date1 and input_date2:
    # Process the first file.
    processed_data1 = None
    if uploaded_file1:
        processed_data1 = process_file(uploaded_file1, input_date1)
        if not processed_data1.empty:
            st.write("Processed Data for the First File", processed_data1)
    
    # Process the second file.
    processed_data2 = None
    if uploaded_file2:
        processed_data2 = process_file(uploaded_file2, input_date2)
        if not processed_data2.empty:
            st.write("Processed Data for the Second File", processed_data2)
    
    # Ensure both data frames are valid before comparing.
    if processed_data1 is not None and processed_data2 is not None and not processed_data1.empty and not processed_data2.empty:
        comparison_df = compare_numeric_columns(processed_data1, processed_data2)

# Use isinstance to check if comparison_df is indeed a DataFrame before checking if it's empty.
if isinstance(comparison_df, pd.DataFrame) and not comparison_df.empty:
    st.write("Comparison Results", comparison_df)
    csv_comparison = comparison_df.to_csv(index=True).encode('utf-8')
    st.download_button("Download comparison data as CSV", data=csv_comparison, file_name='comparison_data.csv', mime='text/csv')
else:
    st.error("No comparison results to display.")
