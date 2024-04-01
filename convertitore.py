import streamlit as st
import pandas as pd
import numpy as np

def process_file(file):
    # Read the Excel file
    df = pd.read_excel(file)
    
    # Drop the specified columns including any 'Box' related columns
    columns_to_drop = ['Dim', 'Box. Weekend', 'Box. Week', 'Start Date', 'End Date']
    df = df.drop(columns=[col for col in df.columns if 'Box' in col or col in columns_to_drop], errors='ignore')
    
    if 'Start Date' in df.columns:
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        most_frequent_start_date = df['Start Date'].mode()[0]  # Get the most common start date
        formatted_date = most_frequent_start_date.strftime('%d/%m/%Y')  # Format date
        # Replace 'Adm' in column names with the formatted date
        df = df.rename(columns=lambda x: x.replace('Adm', formatted_date) if 'Adm' in x else x)
    
    # Ensuring the data for pivot table operation is numeric
    for col in df.columns:
        if col not in ['Cinema', 'Title'] and df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert to numeric, coerce errors to NaN
    
    # Creating pivot table
    if 'Cinema' in df.columns and 'Title' in df.columns:
        # Identifying columns that can be pivoted (numeric and not part of the index)
        pivot_columns = [col for col in df.columns if col not in ['Cinema', 'Title']]
        
        if pivot_columns:
            # Aggregate function as sum, but you might need to adjust based on your data
            df_pivot = pd.pivot_table(df, values=pivot_columns, index=['Cinema', 'Title'], aggfunc=np.sum)
            return df_pivot
        else:
            st.error("No suitable columns found for pivoting.")
            return pd.DataFrame()
    else:
        st.error("Essential columns for pivoting ('Cinema' or 'Title') are missing.")
        return pd.DataFrame()

# Streamlit UI
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
