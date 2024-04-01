import streamlit as st
import pandas as pd
import numpy as np

def process_file(file):
    # Read the Excel file
    df = pd.read_excel(file)
    
    # Drop the specified columns including any 'Box' related columns
    columns_to_drop = ['Dim', 'Box. Weekend', 'Box. Week']
    df = df.drop(columns=[col for col in df.columns if 'Box' in col or col in columns_to_drop], errors='ignore')
    
    # Check if 'Start Date' column is present for date manipulation
    if 'Start Date' in df.columns:
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        most_frequent_start_date = df['Start Date'].mode()[0]  # Get the most common start date
        formatted_date = most_frequent_start_date.strftime('%d/%m/%Y')  # Format date
        # Replace 'Adm' in column names with the formatted date
        df = df.rename(columns=lambda x: x.replace('Adm', formatted_date) if 'Adm' in x else x)

    # Drop 'Start Date' and 'End Date' after processing
    df = df.drop(columns=['Start Date', 'End Date'], errors='ignore')
    
    # Convert columns to numeric where applicable for the pivot table operation
    for col in df.columns:
        if col not in ['Cinema', 'Title'] and df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Create the pivot table
    if 'Cinema' in df.columns and 'Title' in df.columns:
        pivot_columns = [col for col in df.columns if col not in ['Cinema', 'Title']]
        
        if pivot_columns:
            df_pivot = pd.pivot_table(df, values=pivot_columns, index=['Cinema', 'Title'], aggfunc=np.sum)

            # Attempt to sort the pivot table's columns by day of the week, starting with Wednesday
            try:
                # Filter out columns that can be converted to dates, avoiding conversion errors
                valid_date_columns = [col for col in df_pivot.columns if pd.to_datetime(col, format='%d/%m/%Y', errors='coerce') is not pd.NaT]
                
                # Sort valid date columns based on the weekday, starting with Wednesday
                sorted_columns = sorted(valid_date_columns, key=lambda x: (pd.to_datetime(x, format='%d/%m/%Y').weekday() + 2) % 7)
                # Include non-date columns if there are any, maintaining their original order
                non_date_columns = [col for col in df_pivot.columns if col not in valid_date_columns]
                df_pivot = df_pivot.reindex(columns=sorted_columns + non_date_columns)
            except Exception as e:
                st.error(f"An error occurred while sorting the columns: {e}")
            
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

