import streamlit as st
import pandas as pd
import numpy as np

def process_file(file):
    # Read the Excel file
    df = pd.read_excel(file)
    
    # Preliminary processing to drop specified columns, including any 'Box' related columns
    columns_to_drop = ['Dim', 'Box. Weekend', 'Box. Week']
    df = df.drop(columns=[col for col in df.columns if 'Box' in col or col in columns_to_drop], errors='ignore')
    
    # Assuming 'Start Date' column is present and used for identifying the week sequence
    if 'Start Date' in df.columns:
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        
        # Ensure all dates are shifted to start the week on Wednesday
        # Note: This step needs clarity. Assuming we use the most frequent 'Start Date' for column renaming
        most_frequent_start_date = df['Start Date'].mode()[0]
        formatted_dates = most_frequent_start_date.strftime('%d/%m/%Y')
        
        # Rename 'Adm' columns to formatted dates
        df = df.rename(columns=lambda x: x.replace('Adm', formatted_dates) if 'Adm' in x else x)

    # Drop 'Start Date' and 'End Date'
    df = df.drop(columns=['Start Date', 'End Date'], errors='ignore')
    
    # Convert columns to numeric for pivot operation
    for col in df.columns:
        if col not in ['Cinema', 'Title'] and df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Create the pivot table
    if 'Cinema' in df.columns and 'Title' in df.columns:
        pivot_columns = [col for col in df.columns if col not in ['Cinema', 'Title']]
        
        if pivot_columns:
            df_pivot = pd.pivot_table(df, values=pivot_columns, index=['Cinema', 'Title'], aggfunc=np.sum)
            
            # Sort the columns by weekday, starting with Wednesday
            df_pivot = df_pivot.reindex(sorted(df_pivot.columns, key=lambda x: (pd.to_datetime(x, format='%d/%m/%Y').weekday() + 2) % 7), axis=1)
            
            return df_pivot
        else:
            st.error("No suitable columns found for pivoting.")
            return pd.DataFrame()
    else:
        st.error("Essential columns for pivoting ('Cinema' or 'Title') are missing.")
        return pd.DataFrame()

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

