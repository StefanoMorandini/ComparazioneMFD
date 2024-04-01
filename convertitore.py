import streamlit as st
import pandas as pd
from datetime import timedelta

def rename_columns_based_on_input_date(df, input_date):
    original_columns = ['Adm. Wed', 'Amd. Thu', 'Adm. Fri', 'Adm. Sat', 'Adm. Sun', 'Adm. Mon', 'Adm. Tue']
    rename_dict = {}
    for i, col in enumerate(original_columns):
        new_name = (input_date + timedelta(days=i)).strftime('%Y-%m-%d')
        rename_dict[col] = new_name
    return df.rename(columns=rename_dict), list(rename_dict.values())

def create_pivot_table(df):
    pivot_columns = [col for col in df.columns if pd.to_datetime(col, format='%d/%m/%Y', errors='coerce') is not pd.NaT and col not in ['Cinema', 'Title']]
    if pivot_columns:
        df_pivot = pd.pivot_table(df, values=pivot_columns, index=['Cinema', 'Title'], aggfunc=np.sum)
        df_pivot = df_pivot.reindex(sorted(df_pivot.columns, key=lambda x: pd.to_datetime(x, format='%d/%m/%Y')), axis=1)
        return df_pivot
    return df

def add_total_row(df):
    # Calculate the total for each column
    total_row = df.sum(numeric_only=True)
    # Ensure 'Total' is a DataFrame with the same columns as df for appending
    total_df = pd.DataFrame(total_row).transpose()
    total_df.index = ['Total']
    # Append total_df to df
    df_with_total = pd.concat([df, total_df])
    return df_with_total


def process_file(file, input_date):
    df = pd.read_excel(file)
    columns_to_drop = ['Dim', 'Box. Weekend', 'Box. Week', 'Start Date', 'End Date', 'TT', 'Distr.', 'Dim.', 'MT', 'Adm. Week', 'Adm. Weekend', 'Adm. Comp. Week', 'Adm. Wedn']
    df = df.drop(columns=[col for col in df.columns if col in columns_to_drop or 'Box' in col], errors='ignore')
    df.set_index('Cinema', inplace=True)
    
    df, new_column_names = rename_columns_based_on_input_date(df, input_date)
    df['Sum of Renamed Columns'] = df[new_column_names].sum(axis=1)
    df = add_total_row(df)

    
    df_pivot = create_pivot_table(df)
    return df_pivot




# Streamlit UI setup
st.title('Comparing Analysis')

# First file uploader
input_date1 = st.date_input("Select the start date for renaming 'Adm' columns for the first file:", value=pd.to_datetime('today'), key='date1')
uploaded_file1 = st.file_uploader("Choose the first Excel file", type=['xlsx'], key='file1')

# Second file uploader
input_date2 = st.date_input("Select the start date for renaming 'Adm' columns for the second file:", value=pd.to_datetime('today'), key='date2')
uploaded_file2 = st.file_uploader("Choose the second Excel file", type=['xlsx'], key='file2')

# Process the first uploaded file
if uploaded_file1 is not None and input_date1:
    processed_data1 = process_file(uploaded_file1, input_date1)
    if not processed_data1.empty:
        st.write("Processed Data Pivot Table for the First File", processed_data1)
        csv1 = processed_data1.to_csv(index=True).encode('utf-8')
        st.download_button("Download processed data as CSV for the first file", data=csv1, file_name='processed_pivot_data1.csv', mime='text/csv', key='download1')
    else:
        st.error("Processing of the first file failed or resulted in an empty DataFrame.")

# Process the second uploaded file
if uploaded_file2 is not None and input_date2:
    processed_data2 = process_file(uploaded_file2, input_date2)
    if not processed_data2.empty:
        st.write("Processed Data Pivot Table for the Second File", processed_data2)
        csv2 = processed_data2.to_csv(index=True).encode('utf-8')
        st.download_button("Download processed data as CSV for the second file", data=csv2, file_name='processed_pivot_data2.csv', mime='text/csv', key='download2')
    else:
        st.error("Processing of the second file failed or resulted in an empty DataFrame.")



def compare_numeric_columns(df1, df2):
    # Ensure the indices of df1 and df2 match; adjust if necessary
    # Assuming 'Cinema' is the index for both DataFrames
    df1.set_index('Cinema', inplace=True)
    df2.set_index('Cinema', inplace=True)

    # Initialize an empty DataFrame for the comparison results
    comparison_df = pd.DataFrame(index=df1.index)

    # Iterate through the columns in df1
    for col in df1.columns:
        if df1[col].dtype in ['int64', 'float64'] and col in df2.columns and df2[col].dtype in ['int64', 'float64']:
            # Ensure only to compare rows where non-numeric data match
            # This step assumes there's a way to identify non-numeric columns; here we check column data types directly
            mask = (df1.select_dtypes(exclude=['int64', 'float64']) == df2.select_dtypes(exclude=['int64', 'float64'])).all(axis=1)
            comparison_df[col] = None  # Initialize the column in the comparison DataFrame
            comparison_df.loc[mask, col] = df1.loc[mask, col] - df2.loc[mask, col]  # Compute the difference for matching rows

    return comparison_df

# Assuming df1 and df2 are your DataFrames after processing
if uploaded_file1 is not None and uploaded_file2 is not None:
    processed_data1 = process_file(uploaded_file1, input_date1)
    processed_data2 = process_file(uploaded_file2, input_date2)
    
    # Comparing the DataFrames
    comparison_df = compare_numeric_columns(processed_data1, processed_data2)
    
    # Displaying and allowing download of the comparison DataFrame
    if not comparison_df.empty:
        st.write("Comparison Results", comparison_df)
        csv_comparison = comparison_df.to_csv().encode('utf-8')
        st.download_button("Download comparison data as CSV", data=csv_comparison, file_name='comparison_data.csv', mime='text/csv')
    else:
        st.error("No comparison results to display.")


