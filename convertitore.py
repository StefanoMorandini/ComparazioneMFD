import streamlit as st
import pandas as pd
from datetime import timedelta, datetime
import matplotlib.pyplot as plt
from pandas.plotting import table
import base64
from tempfile import NamedTemporaryFile

# Function to rename columns based on the input date and correct the "Amd. Thu" to "Adm. Thu"
def rename_columns_based_on_input_date(df, input_date):
    days_of_week = ['Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday']
    if 'Amd. Thu' in df.columns:
        df.rename(columns={'Amd. Thu': 'Adm. Thu'}, inplace=True)
    for i, day in enumerate(days_of_week):
        col_name = f"Adm. {days_of_week[i][:3]}"
        new_name = day
        if col_name in df.columns:
            df.rename(columns={col_name: new_name}, inplace=True)
    return df

# Initialize an empty DataFrame for region totals
region_totals_df = pd.DataFrame()




def create_region_totals_df(df):
    if 'L.R.' not in df.columns:
        st.error("The DataFrame does not contain 'L.R.' column.")
        return pd.DataFrame()
    
    day_columns = ['Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday']
    columns_of_interest = ['L.R.'] + day_columns
    df_filtered = df[columns_of_interest]
    df_totals = df_filtered.groupby('L.R.').sum()
    df_totals['Total'] = df_totals.sum(axis=1)
    
    return df_totals

# Function to process the uploaded file
def process_file(file, input_date):
    df = pd.read_excel(file)
    columns_to_drop = ['Dim', 'Box. Weekend', 'Box. Week', 'Start Date', 'End Date', 'TT', 'Distr.', 'Dim.', 'MT', 'Adm. Week', 'Adm. Weekend', 'Adm. Comp. Week', 'Adm. Wedn']
    df = df.drop(columns=[col for col in df.columns if col in columns_to_drop or 'Box' in col], errors='ignore')
    df = rename_columns_based_on_input_date(df, pd.to_datetime(input_date))
    
    if 'Cinema' in df.columns:
        df = df.groupby('Cinema', as_index=False).sum()
        totals = df.sum(numeric_only=True)
        totals['Cinema'] = 'Total'
        df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)
        df.set_index('Cinema', inplace=True)
    else:
        st.error("'Cinema' column not found. Please check your file.")
        return pd.DataFrame()
    return df

def compare_numeric_columns(df1, df2):
    df1, df2 = df1.align(df2, join='inner', axis=0)
    comparison_results = pd.DataFrame(index=df1.index)
    for col in df1.select_dtypes(include=['number']).columns.intersection(df2.select_dtypes(include=['number']).columns):
        comparison_results[f'{col}_diff'] = df1[col] - df2[col]
    
    comparison_results['Total_diff'] = comparison_results.sum(axis=1)

    return comparison_results

# Function to dynamically get unique L.R. values from a file
def get_unique_lr_values(file):
    df_temp = pd.read_excel(file)
    if 'L.R.' in df_temp.columns:
        return sorted(df_temp['L.R.'].dropna().unique().tolist())
    return []


def find_new_entries(df1, df2):
    # Assuming both DataFrames have a common identifier column named 'Cinema'
    # Adjust 'Cinema' to your specific identifier column if it's named differently
    merged_df = df1.merge(df2, on='Cinema', how='outer', indicator=True)
    new_entries = merged_df[merged_df['_merge'] == 'left_only']
    
    # Optionally, drop the merge indicator column and any columns from df2 if not needed
    new_entries = new_entries.drop(columns=[col for col in new_entries.columns if col.endswith('_y') or col == '_merge'])
    
    # Rename columns ending with '_x' to their original names (from df1)
    new_entries.columns = [col.rstrip('_x') if col.endswith('_x') else col for col in new_entries.columns]
    new_entries['Totale'] = new_entries.sum(axis=1)

    
    return new_entries

st.title('Comparazione andamento cinema di settimana in settimana')

input_date1 = st.date_input("Seleziona il mercoledì della data che vuoi avere come riferimento:", value=pd.to_datetime('today'), key='date1')
uploaded_file1 = st.file_uploader("Choose the first Excel file", type=['xlsx'], key='file1')


input_date2 = st.date_input("Seleziona il mercoledì della settimana con cui vuoi comparare i risultati:", value=pd.to_datetime('today'), key='date2')
uploaded_file2 = st.file_uploader("Choose the second Excel file", type=['xlsx'], key='file2')

if uploaded_file1 and uploaded_file2 and input_date1 and input_date2:
    processed_data1 = process_file(uploaded_file1, input_date1)
    processed_data2 = process_file(uploaded_file2, input_date2)

    if not processed_data1.empty and not processed_data2.empty:
        new_entries_df = find_new_entries(processed_data1, processed_data2)
        
        if not new_entries_df.empty:
            st.write("New Entries exclusive to the first document", new_entries_df)
        

    
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


if uploaded_file1:
    processed_data1 = process_file(uploaded_file1, input_date1)
    
    # Now ensure processed_data1 exists and has data before attempting to create region_totals_df
    if processed_data1 is not None and not processed_data1.empty:
        region_totals_df = create_region_totals_df(processed_data1)
    
    # The .empty check can now safely proceed since region_totals_df is guaranteed to be defined
    if not region_totals_df.empty:
        st.write("Totals for each L.R. from the first document", region_totals_df)
    else:
        st.error("No L.R. totals to display or the document does not contain 'L.R.' column.")
else:
    st.error("Please upload the first document.")







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






