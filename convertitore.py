import streamlit as st
import pandas as pd
from datetime import timedelta

def rename_columns_based_on_input_date(df, input_date):
    current_date = pd.to_datetime(input_date)
    adm_days = ['Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue']
    rename_dict = {}
    for i, day in enumerate(adm_days):
        adm_col_name = f"Adm {day.lower()}"  # Adjust based on actual column names
        if adm_col_name in df.columns:
            rename_dict[adm_col_name] = (current_date + timedelta(days=i)).strftime('%d/%m/%Y')
    return df.rename(columns=rename_dict)

def create_pivot_table(df):
    pivot_columns = [col for col in df.columns if pd.to_datetime(col, format='%d/%m/%Y', errors='coerce') is not pd.NaT and col not in ['Cinema', 'Title']]
    if pivot_columns:
        df_pivot = pd.pivot_table(df, values=pivot_columns, index=['Cinema', 'Title'], aggfunc=np.sum)
        # Sorting pivot columns by date
        df_pivot = df_pivot.reindex(sorted(df_pivot.columns, key=lambda x: pd.to_datetime(x, format='%d/%m/%Y')), axis=1)
        return df_pivot
    return df  # Return original if no pivotable columns found

def process_file(file, input_date):
    df = pd.read_excel(file)
    
    # Initial preprocessing
    columns_to_drop = ['Dim', 'Box. Weekend', 'Box. Week', 'Start Date', 'End Date']
    df = df.drop(columns=[col for col in df.columns if col in columns_to_drop or 'Box' in col], errors='ignore')
    
    df = rename_columns_based_on_input_date(df, input_date)
    
    df_pivot = create_pivot_table(df)
    return df_pivot

# Streamlit UI
st.title('Cinema Data Processor with Date Selection')

# User inputs
input_date = st.date_input("Select the start date for renaming 'Adm' columns:")
uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])

if uploaded_file is not None and input_date:
    processed_data = process_file(uploaded_file, input_date)
    
    if not processed_data.empty:
        st.write("Processed Data Pivot Table", processed_data)
        
        # Convert pivot table to CSV for download
        csv = processed_data.to_csv(index=True).encode('utf-8')
        st.download_button(
            label="Download processed data as CSV",
            data=csv,
            file_name='processed_pivot_data.csv',
            mime='text/csv',
        )
    else:
        st.error("Processing failed or resulted in an empty DataFrame.")



