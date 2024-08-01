import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, date
import base64
import hashlib

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Admin credentials (in a real application, store these securely)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = hash_password("password123")  # Change this to a secure password

# Function to add background image and set table style
def add_bg_from_local(image_file):
    # ... (keep the existing function as is)

# Streamlit app
st.title("Site Data Viewer")

# Session state to keep track of admin login
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# Admin login form
if not st.session_state.admin_logged_in:
    st.subheader("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == ADMIN_USERNAME and hash_password(password) == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("Logged in successfully!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")
else:
    # Add background image
    add_bg_from_local('logo1.png')

    # Logout button
    if st.button("Logout"):
        st.session_state.admin_logged_in = False
        st.experimental_rerun()

    # Rest of the application logic
    # Initialize an empty DataFrame for combined data
    combined_df = pd.DataFrame()

    # Upload Excel files
    uploaded_files = st.file_uploader("Upload Excel files", accept_multiple_files=True, type=["xlsx"])

    if uploaded_files:
        # Process each uploaded file
        for uploaded_file in uploaded_files:
            # Read the Excel file into a DataFrame
            df = pd.read_excel(uploaded_file)
            
            # Determine the provider from the file name
            provider = uploaded_file.name.split('.')[0]
            df['Provider'] = provider
            
            # Append to the combined DataFrame
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    # Check if combined_df is not empty before proceeding
    if not combined_df.empty:
        # Reorder columns to have 'Provider' before 'Sl.No'
        columns_order = ['Provider'] + [col for col in combined_df.columns if col != 'Provider']
        combined_df = combined_df[columns_order]

        # Ensure the 'Date' column is in datetime format
        combined_df['Date'] = pd.to_datetime(combined_df['Date'])

        # Function to retrieve data based on filters
        def get_filtered_data(site_number, date, region, cluster_manager, area_manager, area_executive):
            # ... (keep the existing function as is)

        # Create input field for site number
        site_number = st.text_input("Enter site number:")

        # Create a date input with a minimum date of January 1, 2001
        min_date = date(2001, 1, 1)
        max_date = date.today()
        selected_date = st.date_input("Select date:", min_value=min_date, max_value=max_date, value=max_date, format="DD/MM/YYYY")

        # Create select boxes for Region, Cluster Manager (L1), Area Manager (L2), and Area Executive (L3)
        regions = combined_df['Region'].unique()
        region = st.selectbox("Select Region:", options=[""] + list(regions))

        cluster_managers = combined_df['Cluster MANAGER (L1)'].unique()
        cluster_manager = st.selectbox("Select Cluster Manager (L1):", options=[""] + list(cluster_managers))

        area_managers = combined_df['Area MANAGER (L2)'].unique()
        area_manager = st.selectbox("Select Area Manager (L2):", options=[""] + list(area_managers))

        area_executives = combined_df['Area EXECUTIVE (L3)'].unique()
        area_executive = st.selectbox("Select Area Executive (L3):", options=[""] + list(area_executives))

        # Retrieve and display data based on filters
        data = get_filtered_data(site_number, selected_date, region, cluster_manager, area_manager, area_executive)
        if not data.empty:
            st.write(f"Data for site number: {site_number} on {selected_date.strftime('%d-%m-%Y')}")
            st.dataframe(data.style.set_properties(**{
                'background-color': 'white',
                'color': 'black',
                'border': '1px solid #d3d3d3',
                'text-align': 'left',
                'padding': '8px'
            }).set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#f0f2f6'), ('color', 'black'), ('border', '1px solid #d3d3d3'), ('padding', '8px')]},
                {'selector': 'td', 'props': [('border', '1px solid #d3d3d3'), ('padding', '8px')]}
            ]))
            
            # Option to download the data as an Excel file
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                data.to_excel(writer, index=False, sheet_name='Sheet1')
            processed_data = output.getvalue()
            
            st.download_button(label="Download data as Excel",
                               data=processed_data,
                               file_name='site_data.xlsx',
                               mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        else:
            st.write("No data found for the given filters.")
    else:
        st.write("Please upload Excel files to proceed.")
