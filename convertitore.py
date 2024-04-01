from datetime import timedelta
import pandas as pd
import numpy as np
import streamlit as st

def rename_columns_based_on_date_sequence(df, start_date):
    # Assuming start_date is a pandas Timestamp or datetime object
    # Ensure 'current_date' is properly initialized from 'start_date'
    current_date = start_date
    
    # Create a mapping for renaming columns
    rename_dict = {}
    
    # Example 'Adm' columns naming pattern: 'Adm Wed', 'Adm Thu', etc.
    # This needs to be aligned with your actual column names and how they should progress
    adm_days = ['Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue']
    
    for day in adm_days:
        adm_col_name = f"Adm {day}"  # Constructing column name based on pattern
        if adm_col_name in df.columns:
            rename_dict[adm_col_name] = current_date.strftime('%d/%m/%Y')
            current_date += timedelta(days=1)  # Correctly increment date by one day
    
    return df.rename(columns=rename_dict)

def process_file(file):
    # Read the Excel file
    df = pd.read_excel(file)
    
    # Preliminary processing...
    
    # Assume 'Start Date' exists and is used to calculate the renaming sequence
    if 'Start Date' in df.columns:
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        most_frequent_start_date = df['Start Date'].mode()[0]
        df = rename_columns_based_on_date_sequence(df, most_frequent_start_date)
    
    # Drop 'Start Date' and 'End Date' after processing
    df = df.drop(columns=['Start Date', 'End Date'], errors='ignore')
    
    # Further processing to create pivot table...
    # Note: Ensure pivot table creation and column sorting logic is correctly implemented

    return df  # or return the pivot table if created within this function

# Streamlit UI setup
st.title('Cinema Data Processor')

uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])

if uploaded_file is not None:
    processed_data = process_file(uploaded_file)
    
    if not processed_data.empty:
        st.write("Processed Data Pivot Table", processed_data)
        
        # Convert pivot table to CSV for download
        csv = processed_data.to_csv().encode('utf-8')
        st.download_button(
            label="Download pivot table as CSV",
            data=csv,
            file_name='pivot_table.csv',
            mime='text/csv',
        )
    else:
        st.error("Processing failed. Please ensure the file is correctly formatted.")


