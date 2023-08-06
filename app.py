import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

# Web App Title
st.markdown('''
# **Supplier Inbound Time**

---
''')

# Create a custom SessionState class to handle data persistence
class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

#Function to create a new ID from every row
def create_id(row_index):
    return f'ID{row_index + 1:03}'

#Function to create a grouping day
def grouping_day(Hari):
    if isinstance(Hari, str) and Hari.strip() != '':
        if Hari in ['Senin - Jumat', 'Senin - Sabtu']:
            return Hari
        else:
            return 'Other'
    else:
        return ''

# Function to create a grouping time
def grouping_time(Waktu):
    if Waktu == '07:00 - 17:00':
        return 'Pagi, Siang, Sore'
    elif Waktu == '08:00 - 11:00':
        return 'Pagi'
    elif Waktu == '08:00 - 12:00':
        return 'Pagi'
    elif Waktu == '08:00 - 14:00':
        return 'Pagi, Siang'
    elif Waktu == '08:00 - 15:00':
        return 'Pagi, Siang'
    elif Waktu == '08:00 - 16:00':
        return 'Pagi, Siang'
    elif Waktu == '08:00 - 17.00':
        return 'Pagi, Siang, Sore'
    elif Waktu == '08:00 - 18:00':
        return 'Pagi, Siang, Sore'
    elif Waktu == '08:00 - 20:00':
        return 'Pagi, Siang, Sore, Malam'
    elif Waktu == '09:00 - 10:00':
        return 'Pagi'
    elif Waktu == '09:00 - 11:00':
        return 'Pagi'
    elif Waktu == '09:00 - 16:00':
        return 'Pagi, Siang'
    elif Waktu == '09:00 - 17:00':
        return 'Pagi, Siang, Sore'
    elif Waktu == '10:00 - 11:00':
        return 'Pagi'
    elif Waktu == '10:00 - 14:00':
        return 'Pagi, Siang'
    elif Waktu == '10:00 - 16:00':
        return 'Pagi, Siang'
    elif Waktu == '11:00 - 13:00':
        return 'Siang'
    elif Waktu == '11:00 - 14:00':
        return 'Siang'
    elif Waktu == '12:00 - 15:00':
        return 'Siang'
    elif Waktu == '12:00 - 18:00':
        return 'Siang, Sore'
    elif Waktu == '13:00 - 14:00':
        return 'Siang'
    elif Waktu == '13:00 - 20:00':
        return 'Siang, Sore, Malam'
    elif Waktu == '14:00 - 15:00':
        return 'Siang'
    elif Waktu ==  '15:00 - 18:00':
        return 'Sore'
    else:
        return ''

# Function to add detail time
def add_note (Groping_Time):
    if Groping_Time == 'Pagi':
        return 'Pagi (08:00 - 12:00)'
    elif Groping_Time == 'Siang':
        return 'Siang (12:00 - 15:00)'
    elif Groping_Time == 'Sore':
        return 'Sore (15:00 - 18:00)'
    elif Groping_Time == 'Malam':
        return 'Malam (15:00 - 18:00)'
    else:
        return ''

# Function to update data from the uploaded file
def update_data(uploaded_file):
    global session_state  # Add this line to define session_state as a global variable
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        
        # Data preparation
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        df['Supplier Name'] = df['Supplier Name'].str.upper()
        df['ID'] = df.index.map(create_id)
        df['Grouping Day'] = df['Hari'].apply(grouping_day)
        df['Grouping Time'] = df['Waktu'].apply(grouping_time)
        df = df.assign(Split_Time=df['Grouping Time'].str.split(', ')).explode('Split_Time')
        df['Detail Time'] = df['Split_Time'].apply(add_note)
        
        session_state.df = df   
        session_state.last_search_term = ""  # Reset last_search_term
    else:
        st.info('Awaiting for Excel file to be uploaded.')

# Upload Excel data
uploaded_file = st.sidebar.file_uploader("Upload your input Excel file", type=["xlsx", "xls"])  

# Initialize session_state
session_state = SessionState(df=pd.DataFrame(), last_search_term="")

# Check if data exists before displaying search input
if uploaded_file is not None:
    update_data(uploaded_file)
    
    # Display the data table
    if session_state.df is not None:
        # Create a copy of the DataFrame for filtering
        filtered_data = session_state.df.copy()
        
        # Search bar in the sidebar
        st.sidebar.subheader("Search Data")
        search_term = st.sidebar.text_input("Enter search term:")
    
        # Filter data based on the search term
        if search_term:
            search_term_lower = search_term.lower()
            filtered_data = session_state.df[
                    (session_state.df['Supplier Code'].astype(str).str.contains(search_term_lower)) |
                    (session_state.df['Supplier Name'].astype(str).str.lower().str.contains(search_term_lower)) |
                    (session_state.df['Group Gudang'].astype(str).str.lower().str.contains(search_term_lower)) |
                    (session_state.df['Creator PO'].astype(str).str.lower().str.contains(search_term_lower))
            ]
        else:
            filtered_data = session_state.df

        # Filter by Warehouse (Group Gudang) using slicer with checkboxes
        st.sidebar.subheader("Warehouse")
        selected_warehouse = st.sidebar.multiselect("Select Warehouses", session_state.df['Group Gudang'].unique())
        if selected_warehouse:
            filtered_data = filtered_data[filtered_data['Group Gudang'].isin(selected_warehouse)]

        # Filter by Day (Grouping Day) using slicer with checkboxes
        st.sidebar.subheader("Day")
        selected_day = st.sidebar.multiselect("Select Days", ['Senin - Jumat', 'Senin - Sabtu', 'Other'])
        if selected_day:
            filtered_data = filtered_data[filtered_data['Grouping Day'].isin(selected_day)]

        # Filter by Inbound Time (Split_Time) using slicer with checkboxes
        st.sidebar.subheader("Inbound Time")
        selected_time = st.sidebar.multiselect("Select Inbound Times", ['Pagi', 'Siang', 'Sore', 'Malam'])
        if selected_time:
            filtered_data = filtered_data[filtered_data['Split_Time'].isin(selected_time)]

        # Display the filtered data
        if not selected_warehouse and not selected_day and not selected_time:
            st.write("Data:")
            st.dataframe(filtered_data[['Merchant Type', 'Supplier Code', 'Supplier Name', 'Group Gudang', 'Creator PO',
                                        'Minimum Order Quantity (MOQ)', 'Carton / Pcs / Value', 'MOQ in carton/ pcs / value;  Jika NO isikan dengan 1', 'TGR N - Neglasari', 'TGR E - Batu Ceper', 'BOO N - Bogor', 'CGK SE - Kramat Jati', 'BKI NW - Medan Satria', 'BKI E - Cikarang', 'SMG SE - Semarang', 'SMG W - Semarang Barat', 'SOC E - Karanganyar', 'JOG NE - Sleman', 'BDG E - Bandung Kiaracondong', 'UPG N - Makassar',
                                        'MES E - Deli Serdang', 'MES S - Medan', 'SUB S - Sidoardjo', 'Hari', 'Waktu']])
        else:
            st.write("Filtered Data:")
            st.dataframe(filtered_data[['Merchant Type', 'Supplier Code', 'Supplier Name', 'Group Gudang', 'Creator PO',
                                        'Minimum Order Quantity (MOQ)', 'Carton / Pcs / Value', 'MOQ in carton/ pcs / value;  Jika NO isikan dengan 1', 'TGR N - Neglasari', 'TGR E - Batu Ceper', 'BOO N - Bogor', 'CGK SE - Kramat Jati', 'BKI NW - Medan Satria', 'BKI E - Cikarang', 'SMG SE - Semarang', 'SMG W - Semarang Barat', 'SOC E - Karanganyar', 'JOG NE - Sleman', 'BDG E - Bandung Kiaracondong', 'UPG N - Makassar',
                                        'MES E - Deli Serdang', 'MES S - Medan', 'SUB S - Sidoardjo', 'Hari', 'Waktu']])

        # Pembersihan data dari nilai kosong atau whitespace menjadi NaN
        filtered_data_cleaned = filtered_data.replace(r'^\s*$', np.nan, regex=True)
        
        # Group data by 'Warehouse Name' and calculate count distinct 'ID'
        warehouse_counts = filtered_data_cleaned.dropna(subset=['Group Gudang']).groupby('Group Gudang')['ID'].nunique().reset_index()

        # Data Visualization
        st.subheader("Data Visualization")
        
        # Number of warehouses distribution with bar chart
        warehouse_distribution = (
            alt.Chart(warehouse_counts)
            .mark_bar()
            .encode(
                x=alt.X('Group Gudang', axis=alt.Axis(title='Warehouse', labelAngle=0)),
                y=alt.Y('ID:Q', axis=alt.Axis(title='Number of Warehouses')),
                tooltip=['Group Gudang']
            )
            .properties(title='Number of Warehouses Distribution')
        )
        st.altair_chart(warehouse_distribution, use_container_width=True)
        
        # Number of Inbound time with bar chart
        inbound_time_distribution = (
            alt.Chart(filtered_data_cleaned.dropna(subset=['Grouping Day']))
            .mark_bar()
            .encode(
                x=alt.X('Grouping Day', axis=alt.Axis(title='Grouping Day', labelAngle=0)),
                y=alt.Y('count()', axis=alt.Axis(title='Number of Inbound Time')),
                color=alt.Color('Detail Time', legend=alt.Legend(title='Detail Time')),
                tooltip=['Grouping Day', 'count()']
            )
            .properties(title='Number of Inbound Time Distribution')
        )
        st.altair_chart(inbound_time_distribution, use_container_width=True)

else:
    st.info('Awaiting for Excel file to be uploaded.')

