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
    if 'Amd. Thu' in df.columns:
        df.rename(columns={'Amd. Thu': 'Adm. Thu'}, inplace=True)
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
 

st.title('Comparazione andamento cinema di settimana in settimana')

input_date1 = st.date_input("Seleziona il mercoledì della data che vuoi avere come riferimento:", value=pd.to_datetime('today'), key='date1')
uploaded_file1 = st.file_uploader("Choose the first Excel file", type=['xlsx'], key='file1')

input_date2 = st.date_input("Seleziona il mercoledì della settimana con cui vuoi comparare i risultati:", value=pd.to_datetime('today'), key='date2')
uploaded_file2 = st.file_uploader("Choose the second Excel file", type=['xlsx'], key='file2')

if uploaded_file1 and uploaded_file2 and input_date1 and input_date2:
    processed_data1 = process_file(uploaded_file1, input_date1)
    processed_data2 = process_file(uploaded_file2, input_date2)
    
    week_start = input_date1.strftime('%d/%m/%Y')
    week_end = (input_date1 + timedelta(days=6)).strftime('%d/%m/%Y')
    results_title = f"Risultati della settimana dal {week_start} al {week_end}"
    
    st.subheader(results_title)
    if not processed_data1.empty and not processed_data2.empty:
        st.write("Risultati della settimana base", processed_data1)
        st.write("Risultati della settimana di riferimento", processed_data2)
        
        comparison_df = compare_numeric_columns(processed_data1.drop(index='Total'), processed_data2.drop(index='Total'))
        if not comparison_df.empty:
            st.write("Risultati della comparazione", comparison_df)
            csv_comparison = comparison_df.to_csv(index=True).encode('utf-8')
            st.download_button("Scarica comparazione in CSV", data=csv_comparison, file_name='comparison_data.csv', mime='text/csv')
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

def df_to_image(df, filename, title=""):
    # Determine the figure size dynamically based on DataFrame dimensions
    fig_size = (max(6, len(df.columns) * 1.5), max(4, len(df) * 0.5) + 0.5)  # Add space for the title
    fig, ax = plt.subplots(figsize=fig_size)
    ax.axis('off')  # Hide axes

    # Place the table on the figure
    tbl = table(ax, df, loc='center', cellLoc='center', colWidths=[0.1]*len(df.columns))
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.2, 1.2)

    # Add title if provided
    if title:
        plt.suptitle(title, fontsize=12)

    plt.savefig(filename, bbox_inches='tight', pad_inches=0.05, dpi=150)
    plt.close()

def get_image_download_link(filepath, filename='dataframe.png'):
    with open(filepath, "rb") as file:
        data = base64.b64encode(file.read()).decode('utf-8')
    href = f'<a href="data:file/png;base64,{data}" download="{filename}">Download as PNG</a>'
    return href

input_date = st.date_input("Select the start date for the DataFrame:")
week_start = input_date.strftime('%d/%m/%Y')
week_end = (input_date + timedelta(days=6)).strftime('%d/%m/%Y')
title = f"Risultati della settimana dal {week_start} al {week_end}"



# Convert DataFrame to PNG and provide a download link
with NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
    df_to_image(comparison_df, tmp_file.name, title=title)
    st.markdown(get_image_download_link(tmp_file.name, 'Comparazione_Cinema_Settimana_{input_date1}.png'), unsafe_allow_html=True)

with NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
    df_to_image(processed_data1, tmp_file.name, title=title)
    st.markdown(get_image_download_link(tmp_file.name, 'Risultati_byDay_ Cinema_Sett_base.png'), unsafe_allow_html=True)


def compare_weekend_columns(df1, df2):
    # Ensure both dataframes are aligned
    df1, df2 = df1.align(df2, join='inner', axis=0)
    
    # Define the weekend days to compare
    weekend_days = ['Friday', 'Saturday', 'Sunday']
    
    # Filter the dataframes to include only the weekend columns
    df1_weekend = df1[weekend_days]
    df2_weekend = df2[weekend_days]
    
    # Initialize the comparison results dataframe
    comparison_results_weekend = pd.DataFrame(index=df1.index)
    
    # Perform the comparison for each weekend day
    for day in weekend_days:
        comparison_results_weekend[f'{day}_diff'] = df1_weekend[day] - df2_weekend[day]
    
    # Add a sum column for the weekend
    comparison_results_weekend['Weekend_Sum'] = comparison_results_weekend.sum(axis=1)
    
    return comparison_results_weekend

# Assuming processed_data1 and processed_data2 are your input DataFrames
if not processed_data1.empty and not processed_data2.empty:
    comparison_weekend_df = compare_weekend_columns(processed_data1, processed_data2)

    if not comparison_weekend_df.empty:
        st.write("Comparison Results for the Weekend", comparison_weekend_df)
        # Further code for downloading or displaying the results...
    else:
        st.error("No comparison results to display for the weekend.")
else:
    st.error("DataFrames are empty or not properly loaded.")





