import streamlit as st
import pandas as pd
from datetime import timedelta

def rename_columns_based_on_input_date(df, input_date):
    original_columns = ['Adm. Wed', 'Adm. Thu', 'Adm. Fri', 'Adm. Sat', 'Adm. Sun', 'Adm. Mon', 'Adm. Tue']
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

def create_pivot_table(df):
    pivot_columns = [col for col in df.columns if pd.to_datetime(col, format='%d/%m/%Y', errors='coerce') is not pd.NaT and col not in ['Cinema', 'Title']]
    if pivot_columns:
        df_pivot = pd.pivot_table(df, values=pivot_columns, index=df.index, aggfunc=np.sum)
        df_pivot = df_pivot.reindex(sorted(df_pivot.columns, key=lambda x: pd.to_datetime(x, format='%d/%m/%Y')), axis=1)
        return df_pivot
    return df

def display_day_of_week_headers(dates):
    days_of_week = [pd.to_datetime(date).strftime('%A') for date in dates]
    st.markdown("### Days of the Week")
    st.text(' | '.join(days_of_week))

# Streamlit UI
st.title('Cinema Data Processor with Date Selection')

# User inputs for the first file
input_date1 = st.date_input("Select the start date for renaming 'Adm' columns for the first file:", value=pd.to_datetime('today'), key='date1')
uploaded_file1 = st.file_uploader("Choose the first Excel file", type=['xlsx'], key='file1')

# Process and display the first file
if uploaded_file1 and input_date1:
    processed_data1 = process_file(uploaded_file1, input_date1)
    processed_pivot1 = create_pivot_table(processed_data1)
    if not processed_pivot1.empty:
        display_day_of_week_headers(processed_pivot1.columns)
        st.write("Processed Data Pivot Table for the First File", processed_pivot1)
        csv1 = processed_pivot1.to_csv(index=True).encode('utf-8')
        st.download_button("Download processed data as CSV for the first file", data=csv1, file_name='processed_pivot_data1.csv', mime='text/csv', key='download1')

# User inputs for the second file
input_date2 = st.date_input("Select the start date for renaming 'Adm' columns for the second file:", value=pd.to_datetime('today'), key='date2')
uploaded_file2 = st.file_uploader("Choose the second Excel file", type=['xlsx'], key='file2')

# Process and display the second file
if uploaded_file2 and input_date2:
    processed_data2 = process_file(uploaded_file2, input_date2)
    processed_pivot2 = create_pivot_table(processed_data2)
    if not processed_pivot2.empty:
        display_day_of_week_headers(processed_pivot2.columns)
        st.write("Processed Data Pivot Table for the Second File", processed_pivot2)
        csv2 = processed_pivot2.to_csv(index=True).encode('utf-8')
        st.download_button("Download processed data as CSV for the second file", data=csv2, file_name='processed_pivot_data2.csv', mime='text/csv', key='download2')

