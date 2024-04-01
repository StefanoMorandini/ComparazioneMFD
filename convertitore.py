import streamlit as st
import pandas as pd
from datetime import timedelta

def rename_columns_based_on_input_date(df, input_date):
    original_columns = ['Adm. Wed', 'Adm. Thu', 'Adm. Fri', 'Adm. Sat', 'Adm. Sun', 'Adm. Mon', 'Adm. Tue']
    rename_dict = {}
    for i, col in enumerate(original_columns):
        new_name = (input_date + timedelta(days=i)).strftime('%Y-%m-%d')
        if col in df.columns:  # Ensure column exists before attempting to rename
            rename_dict[col] = new_name
    return df.rename(columns=rename_dict)

def process_file(file, input_date):
    df = pd.read_excel(file)
    columns_to_drop = ['Dim', 'Box. Weekend', 'Box. Week', 'Start Date', 'End Date', 'TT', 'Distr.', 'Dim.', 'MT', 'Adm. Week', 'Adm. Weekend', 'Adm. Comp. Week', 'Adm. Wedn']
    df = df.drop(columns=[col for col in df.columns if col in columns_to_drop or 'Box' in col], errors='ignore')
    df = rename_columns_based_on_input_date(df, input_date)
    
    if 'Cinema' in df.columns:
        # Group by 'Cinema' and calculate sum for numerical columns
        grouped_df = df.groupby('Cinema').sum()
        # Calculate totals for each numerical column and append as a new row
        totals = grouped_df.sum(numeric_only=True).rename('Total')
        grouped_df = grouped_df.append(totals)
    else:
        st.error("'Cinema' column not found. Please check your file.")
        return pd.DataFrame()
    
    return grouped_df

def compare_numeric_columns(df1, df2):
    df1, df2 = df1.align(df2, join='inner', axis=0)
    comparison_results = pd.DataFrame(index=df1.index)
    for col in df1.select_dtypes(include=['number']).columns:
        if col in df2.columns:
            comparison_results[f'{col}_diff'] = df1[col] - df2[col]
    return comparison_results

# Streamlit UI setup
st.title('Cinema Data Processor with Date Selection and Aggregated Comparison')

input_date1 = st.date_input("Select the start date for renaming 'Adm' columns for the first file:", value=pd.to_datetime('today'), key='date1')
uploaded_file1 = st.file_uploader("Choose the first Excel file", type=['xlsx'], key='file1')

input_date2 = st.date_input("Select the start date for renaming 'Adm' columns for the second file:", value=pd.to_datetime('today'), key='date2')
uploaded_file2 = st.file_uploader("Choose the second Excel file", type=['xlsx'], key='file2')

processed_data1, processed_data2 = None, None

if uploaded_file1 and input_date1:
    processed_data1 = process_file(uploaded_file1, input_date1)
    if not processed_data1.empty:
        st.write("Processed Data for the First File", processed_data1)
        csv1 = processed_data1.to_csv(index=True).encode('utf-8')
        st.download_button("Download processed data as CSV for the first file", data=csv1, file_name='processed_pivot_data1.csv', mime='text/csv', key='download1')

if uploaded_file2 and input_date2:
    processed_data2 = process_file(uploaded_file2, input_date2)
    if not processed_data2.empty:
        st.write("Processed Data for the Second File", processed_data2)
        csv2 = processed_data2.to_csv(index=True).encode('utf-8')
        st.download_button("Download processed data as CSV for the second file", data=csv2, file_name='processed_pivot_data2.csv', mime='text/csv', key='download2')

comparison_df = pd.DataFrame()
if processed_data1 is not None and processed_data2 is not None:
    comparison_df = compare_numeric_columns(processed_data1, processed_data2)

if not comparison_df.empty:
    st.write("Comparison Results", comparison_df)
    csv_comparison = comparison_df.to_csv(index=True).encode('utf-8')
    st.download_button("Download comparison data as CSV", data=csv_comparison, file_name='comparison_data.csv', mime='text/csv')
else:
    st.error("No comparison results to display or one of the files did not process correctly.")

if uploaded_file1 and uploaded_file2 and input_date1 and input_date2:
    processed_data1 = process_file(uploaded_file1, input_date1)
    processed_data2 = process_file(uploaded_file2, input_date2)
    
    # Display the processed data and provide download links...

    comparison_df = pd.DataFrame()
    if not processed_data1.empty and not processed_data2.empty:
        comparison_df = compare_numeric_columns(processed_data1.drop('Total'), processed_data2.drop('Total'))

    if not comparison_df.empty:
        st.write("Comparison Results", comparison_df)
        csv_comparison = comparison_df.to_csv(index=True).encode('utf-8')
        st.download_button("Download comparison data as CSV", data=csv_comparison, file_name='comparison_data.csv', mime='text/csv')
    else:
        st.error("No comparison results to display or one of the files did not process correctly.")
