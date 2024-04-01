import streamlit as st
import pandas as pd

def process_file(file):
    # Read the Excel file
    df = pd.read_excel(file)
    
    # Initial processing to drop specified columns including any 'Box' related columns
    columns_to_drop = ['Dim', 'Box. Weekend', 'Box. Week', 'Start Date', 'End Date']
    df = df.drop(columns=[col for col in df.columns if 'Box' in col or col in columns_to_drop], errors='ignore')
    
    if 'Start Date' in df.columns:
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        most_frequent_start_date = df['Start Date'].mode()[0]  # Get the most common start date
        formatted_date = most_frequent_start_date.strftime('%d/%m/%Y')  # Format date
        # Replace 'Adm' in column names with the formatted date
        df = df.rename(columns=lambda x: x.replace('Adm', formatted_date) if 'Adm' in x else x)
    
    # Assuming you want to pivot on some value columns that you've now renamed to dates
    # First, ensure 'Cinema' and 'Title' are not set as index yet for pivot operation
    if 'Cinema' in df.columns and 'Title' in df.columns:
        # Determine which columns to use for the pivot table (excluding 'Cinema' and 'Title')
        pivot_columns = [col for col in df.columns if col not in ['Cinema', 'Title']]
        # Pivot operation
        df_pivot = pd.pivot_table(df, values=pivot_columns, index=['Cinema', 'Title'], aggfunc=np.sum)
        return df_pivot
    else:
        return pd.DataFrame()  # Return an empty DataFrame if essential columns are missing

# Streamlit UI
st.title('Cinema Data Processor')

uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])

if uploaded_file is not None:
    processed_data = process_file(uploaded_file)
    
    st.write("Processed Data Pivot Table", processed_data)
    
    # Convert pivot table to CSV for download
    csv = processed_data.to_csv().encode('utf-8')
    st.download_button(
        label="Download pivot table as CSV",
        data=csv,
        file_name='pivot_table.csv',
        mime='text/csv',
    )
