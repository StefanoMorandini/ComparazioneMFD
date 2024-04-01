import streamlit as st
import pandas as pd
from datetime import timedelta

def add_sum_column(df):
    # Assuming day-of-the-week columns are all the numeric columns except the 'Total' row
    day_columns = [col for col in df.columns if col in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
    df['Sum'] = df[day_columns].sum(axis=1)
    return df

def rename_columns_based_on_input_date(df, input_date):
    days_of_week = ['Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday']
    for i, day in enumerate(days_of_week):
        # Calculate date for each day of the week based on input_date
        day_date = input_date + timedelta(days=i)
        # Match your actual column names to the new naming convention as needed
        col_name = f"Adm. {days_of_week[i][:3]}"  # Assuming original columns follow this pattern
        new_name = day  # Use full day name as new column name
        if col_name in df.columns:  # Check if the column exists before renaming
            df.rename(columns={col_name: new_name}, inplace=True)
    return df

def process_file(file, input_date):
    df = pd.read_excel(file)
    columns_to_drop = ['Dim', 'Box. Weekend', 'Box. Week', 'Start Date', 'End Date', 'TT', 'Distr.', 'Dim.', 'MT', 'Adm. Week', 'Adm. Weekend', 'Adm. Comp. Week', 'Adm. Wedn']
    df = df.drop(columns=[col for col in df.columns if col in columns_to_drop or 'Box' in col], errors='ignore')
    df = rename_columns_based_on_input_date(df, pd.to_datetime(input_date))
    
    if 'Cinema' in df.columns:
        df = df.groupby('Cinema', as_index=False).sum()  # Group by 'Cinema' and sum numerical columns
        totals = df.sum(numeric_only=True)
        totals['Cinema'] = 'Total'  # Mark this row as 'Total'
        df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)
        df.set_index('Cinema', inplace=True)
        df = add_sum_column(df)

    else:
        st.error("'Cinema' column not found. Please check your file.")
        return pd.DataFrame()
    
    return df

def compare_numeric_columns(df1, df2):
    df1, df2 = df1.align(df2, join='inner', axis=0)  # Align DataFrames based on 'Cinema' index
    comparison_results = pd.DataFrame(index=df1.index)
    for col in df1.select_dtypes(include=['number']).columns.intersection(df2.select_dtypes(include=['number']).columns):
        comparison_results[f'{col}_diff'] = df1[col] - df2[col]  # Calculate differences
    return comparison_results
 

st.title('Cinema Data Processor with Date Selection and Aggregated Comparison')

input_date1 = st.date_input("Select the start date for renaming 'Adm' columns for the first file:", value=pd.to_datetime('today'), key='date1')
uploaded_file1 = st.file_uploader("Choose the first Excel file", type=['xlsx'], key='file1')

input_date2 = st.date_input("Select the start date for renaming 'Adm' columns for the second file:", value=pd.to_datetime('today'), key='date2')
uploaded_file2 = st.file_uploader("Choose the second Excel file", type=['xlsx'], key='file2')

if uploaded_file1 and uploaded_file2 and input_date1 and input_date2:
    processed_data1 = process_file(uploaded_file1, input_date1)
    processed_data2 = process_file(uploaded_file2, input_date2)
    
    week_start = input_date1.strftime('%d/%m/%Y')
    week_end = (input_date1 + timedelta(days=6)).strftime('%d/%m/%Y')
    results_title = f"Risultati della settimana dal {week_start} al {week_end}"
    
    st.subheader(results_title)
    if not processed_data1.empty and not processed_data2.empty:
        st.write("Processed Data for the First File", processed_data1)
        st.write("Processed Data for the Second File", processed_data2)
        
        comparison_df = compare_numeric_columns(processed_data1.drop(index='Total'), processed_data2.drop(index='Total'))
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


import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import table
import base64
import streamlit as st
from tempfile import NamedTemporaryFile

def df_to_image(df, filename):
    # Calculate figure size to somewhat dynamically handle different DataFrame sizes
    fig_size = (max(6, len(df.columns) * 1.5), max(4, len(df) * 0.5))
    fig, ax = plt.subplots(figsize=fig_size)  # Adjust figure size dynamically
    ax.axis('off')  # Hide the axes

    # Create the table and adjust font if needed
    tbl = table(ax, df, loc='center', cellLoc='center', colWidths=[0.1]*len(df.columns))
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)  # Small font size to fit more columns
    tbl.scale(1.2, 1.2)  # Scale table size to make it more readable

    plt.savefig(filename, bbox_inches='tight', pad_inches=0.05, dpi=150)
    plt.close()

def get_image_download_link(filepath, filename='dataframe.png'):
    with open(filepath, "rb") as file:
        data = base64.b64encode(file.read()).decode('utf-8')
    href = f'<a href="data:file/png;base64,{data}" download="{filename}">Download as PNG</a>'
    return href




# Convert DataFrame to PNG and provide a download link
with NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
    df_to_image(comparison_df, tmp_file.name)
    st.markdown(get_image_download_link(tmp_file.name, 'DataFrame.png'), unsafe_allow_html=True)





