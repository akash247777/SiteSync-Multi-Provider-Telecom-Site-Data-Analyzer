# Import required libraries
import streamlit as st  # Streamlit for creating the web app
import pandas as pd  # Pandas for data manipulation and analysis
from io import BytesIO  # BytesIO for handling binary data
from datetime import datetime, date  # Datetime for date and time manipulation
import base64  # Base64 for encoding and decoding binary data

# Function to add background image and set table style
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:  # Open the image file in binary mode
        encoded_string = base64.b64encode(image_file.read())  # Encode the image to base64
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"png"};base64,{encoded_string.decode()});  # Set background image using base64 string
            background-size: cover;  # Cover the entire background
            background-repeat: no-repeat;  # Do not repeat the background image
            background-attachment: local;  # Scroll the background image with the page
        }}
        .main {{
            position: relative;  # Positioning for the main content
            z-index: 2;  # Stack order of the main content
        }}
        .stDataFrame table {{
            background-color: black !important;  # Set table background color
            border-collapse: collapse !important;  # Collapse table borders
            border: 1px solid #050505 !important;  # Set border color and style
        }}
        .stDataFrame th {{
            background-color: #f0f2f6 !important;  # Set table header background color
            border: 1px solid #d3d3d3 !important;  # Set border color and style for headers
            padding: 8px !important;  # Set padding for table headers
        }}
        .stDataFrame td {{
            background-color: black !important;  # Set table cell background color
            border: 1px solid #d3d3d3 !important;  # Set border color and style for cells
            padding: 8px !important;  # Set padding for table cells
        }}
        </style>
        """,
        unsafe_allow_html=True  # Allow HTML in markdown for styling
    )

# Add your background image
add_bg_from_local('logo1.png')  # Call the function with the path to your image

# Streamlit app
st.title("Site Data Viewer")  # Set the title of the app

# Add a selectbox to choose the input method
input_method = st.selectbox("Select Input Method:", ["Upload Files", "Manual Input"])

# Initialize an empty DataFrame for combined data
combined_df = pd.DataFrame()

if input_method == "Upload Files":
    # Upload Excel files
    uploaded_files = st.file_uploader("Upload Excel files", accept_multiple_files=True, type=["xlsx"])

    if uploaded_files:
        # Process each uploaded file
        for uploaded_file in uploaded_files:
            # Read the Excel file into a DataFrame
            df = pd.read_excel(uploaded_file)
            
            # Determine the provider from the file name (assuming the file name contains the provider name)
            provider = uploaded_file.name.split('.')[0]  # Extract provider name from file name
            df['Provider'] = provider  # Add 'Provider' column
            
            # Append to the combined DataFrame
            combined_df = pd.concat([combined_df, df], ignore_index=True)

else:
    # Load the data from the three Excel files manually and add a 'Provider' column
    bsnl_df = pd.read_excel('C:\\Users\\Administrator\\Downloads\\bsnl.xlsx')  # Load BSNL data
    bsnl_df['Provider'] = 'BSNL'  # Add 'Provider' column with value 'BSNL'

    airtel_df = pd.read_excel('C:\\Users\\Administrator\\Downloads\\airtel.xlsx')  # Load Airtel data
    airtel_df['Provider'] = 'Airtel'  # Add 'Provider' column with value 'Airtel'

    vi_df = pd.read_excel('C:\\Users\\Administrator\\Downloads\\vi.xlsx')  # Load VI data
    vi_df['Provider'] = 'VI'  # Add 'Provider' column with value 'VI'

    # Combine the data into a single DataFrame
    combined_df = pd.concat([bsnl_df, airtel_df, vi_df], ignore_index=True)  # Concatenate the dataframes

# Check if combined_df is not empty before proceeding
if not combined_df.empty:
    # Reorder columns to have 'Provider' before 'Sl.No'
    columns_order = ['Provider'] + [col for col in combined_df.columns if col != 'Provider']
    combined_df = combined_df[columns_order]  # Reorder the columns

    # Ensure the 'Date' column is in datetime format
    combined_df['Date'] = pd.to_datetime(combined_df['Date'])  # Convert 'Date' column to datetime format

    # Function to retrieve data based on filters
    def get_filtered_data(site_number, date, region, cluster_manager, area_manager, area_executive):
        filtered_data = combined_df.copy()  # Make a copy of the combined dataframe
        
        if site_number:
            filtered_data = filtered_data[filtered_data['Site'].astype(str).str.contains(str(site_number))]  # Filter by site number
        if date:
            filtered_data = filtered_data[filtered_data['Date'].dt.strftime('%d-%m-%Y') == date.strftime('%d-%m-%Y')]  # Filter by date
        if region:
            filtered_data = filtered_data[filtered_data['Region'] == region]  # Filter by region
        if cluster_manager:
            filtered_data = filtered_data[filtered_data['Cluster MANAGER (L1)'] == cluster_manager]  # Filter by cluster manager
        if area_manager:
            filtered_data = filtered_data[filtered_data['Area MANAGER (L2)'] == area_manager]  # Filter by area manager
        if area_executive:
            filtered_data = filtered_data[filtered_data['Area EXECUTIVE (L3)'] == area_executive]  # Filter by area executive
        
        # Convert the Date column to dd-mm-yyyy format
        filtered_data['Date'] = filtered_data['Date'].dt.strftime('%d-%m-%Y')  # Format the date column
        return filtered_data  # Return the filtered data

    # Create input field for site number
    site_number = st.text_input("Enter site number:")  # Text input for site number

    # Create a date input with a minimum date of January 1, 2001
    min_date = date(2001, 1, 1)  # Minimum date
    max_date = date.today()  # Maximum date is today
    selected_date = st.date_input("Select date:", min_value=min_date, max_value=max_date, value=max_date, format="DD/MM/YYYY")  # Date input field

    # Create select boxes for Region, Cluster Manager (L1), Area Manager (L2), and Area Executive (L3)
    regions = combined_df['Region'].unique()  # Get unique regions
    region = st.selectbox("Select Region:", options=[""] + list(regions))  # Select box for region

    cluster_managers = combined_df['Cluster MANAGER (L1)'].unique()  # Get unique cluster managers
    cluster_manager = st.selectbox("Select Cluster Manager (L1):", options=[""] + list(cluster_managers))  # Select box for cluster manager

    area_managers = combined_df['Area MANAGER (L2)'].unique()  # Get unique area managers
    area_manager = st.selectbox("Select Area Manager (L2):", options=[""] + list(area_managers))  # Select box for area manager

    area_executives = combined_df['Area EXECUTIVE (L3)'].unique()  # Get unique area executives
    area_executive = st.selectbox("Select Area Executive (L3):", options=[""] + list(area_executives))  # Select box for area executive

    # Retrieve and display data based on filters
    data = get_filtered_data(site_number, selected_date, region, cluster_manager, area_manager, area_executive)  # Get filtered data
    if not data.empty:
        st.write(f"Data for site number: {site_number} on {selected_date.strftime('%d-%m-%Y')}")  # Display site number and date
        st.dataframe(data.style.set_properties(**{
            'background-color': 'white',  # Set cell background color
            'color': 'black',  # Set text color
            'border': '1px solid #d3d3d3',  # Set cell border
            'text-align': 'left',  # Align text to the left
            'padding': '8px'  # Set cell padding
        }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#f0f2f6'), ('color', 'black'), ('border', '1px solid #d3d3d3'), ('padding', '8px')]},  # Header styles
            {'selector': 'td', 'props': [('border', '1px solid #d3d3d3'), ('padding', '8px')]}  # Cell styles
        ]))
        
        # Option to download the data as an Excel file
        output = BytesIO()  # Create a BytesIO object
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:  # Write data to Excel
            data.to_excel(writer, index=False, sheet_name='Sheet1')  # Write the dataframe to a sheet
        processed_data = output.getvalue()  # Get the binary data from the BytesIO object
        
        st.download_button(label="Download data as Excel",
                           data=processed_data,
                           file_name='site_data.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  # Add a download button
    else:
        st.write("No data found for the given filters.")  # Display message if no data is found
else:
    st.write("Please upload Excel files or select Manual Input to proceed.")  # Display message to upload files or select manual input
