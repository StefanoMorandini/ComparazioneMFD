import streamlit as st
import pandas as pd
from datetime import timedelta, datetime

def rename_columns_based_on_input_date(df, input_date):
    days_of_week = ['Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday']
    for i, day in enumerate(days_of_week):
        new_name = day
        col_name = f"Adm. {day[:3]}"  # Adjust based on your column naming convention
        if col_name in df.columns:
            df.rename(columns={col_name: new_name}, inplace=True)
    return df

def process_file(file, input_date):
    df = pd.read_excel(file)
    columns_to_drop = ['Dim', 'Box. Weekend', 'Box. Week', 'Start Date', 'End Date', 'TT', 'Distr.', 'Dim.', 'MT', 'Adm. Week', 'Adm. Weekend', 'Adm. Comp. Week', 'Adm. Wedn']
    df = df.drop(columns=[col for col in df.columns if col in columns_to_drop or 'Box' in col], errors='ignore')
    df = rename_columns_based_on_input_date(df, pd.to_datetime(input_date))
    
    if 'Cinema' in df.columns:
        df['Sum of Renamed Columns'] = df.select_dtypes(include=['number']).sum(axis=1)
        grouped_df = df.groupby('Cinema').sum()
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
st.title('Cinema Data Processor with Date Selection and Aggregated Comparison')

input_date1 = st.date_input("Select the start date for renaming 'Adm' columns for the first file:", value=pd.to_datetime('today'), key='date1')
uploaded_file1 = st.file_uploader("Choose the first Excel file", type=['xlsx'], key='file1')

input_date2 = st.date_input("Select the start date for renaming 'Adm' columns for the second file:", value=pd.to_datetime('today'), key='date2')
uploaded_file2 = st.file_uploader("Choose the second Excel file", type=['xlsx'], key='file2')

# Process the files if both are uploaded and input dates are selected
if uploaded_file1 and uploaded_file2 and input_date1 and input_date2:
    processed_data1 = process_file(uploaded_file1, input_date1)
    processed_data2 = process_file(uploaded_file2, input_date2)
    
    week_start = input_date1.strftime('%d/%m/%Y')
    week_end = (input_date1 + timedelta(days=6)).strftime('%d/%m/%Y')
    results_title = f"Risultati della settimana dal {week_start} al {week_end}"
    
    if not processed_data1.empty and not processed_data2.empty:
        st.subheader(results_title)
        comparison_df = compare_numeric_columns(processed_data1.drop('Total'), processed_data2.drop('Total'))

        if not comparison_df.empty:
            st.write("Comparison Results", comparison_df)
            csv_comparison = comparison_df.to_csv(index=True).encode('utf-8')
            st.download_button("Download comparison data as CSV", data=csv_comparison, file_name='comparison_data.csv', mime='text/csv')
        else:
            st.error("No comparison results to display.")
    else:
        st.error("One or both of the files did not process correctly.")
else:
    st.error("Please upload both files and select start dates for each.")




