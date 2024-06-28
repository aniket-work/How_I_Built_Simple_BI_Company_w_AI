import streamlit as st
import os
import sqlite3
import pandas as pd
from pandasai import SmartDataframe
from pandasai.connectors import SqliteConnector
from langchain_groq.chat_models import ChatGroq
from dotenv import load_dotenv
from PIL import Image

# Load environment variables and set constants
load_dotenv()
DATABASE_FOLDER = 'database'
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Initialize GroqLLM
model = ChatGroq(model_name="mixtral-8x7b-32768", api_key=GROQ_API_KEY)


def format_response_to_html_table(response):
    # Split the response into lines
    lines = response.split('\n')

    # Assuming the first line contains headers
    headers = lines[0].split()

    # Start building the HTML table
    html = "<table><tr>"
    for header in headers:
        html += f"<th>{header}</th>"
    html += "</tr>"

    # Add data rows
    for line in lines[1:]:
        html += "<tr>"
        for cell in line.split():
            html += f"<td>{cell}</td>"
        html += "</tr>"

    html += "</table>"
    return html

# Function to get table names
def get_table_names():
    return [os.path.splitext(file)[0] for file in os.listdir(DATABASE_FOLDER) if file.endswith('.db')]

# Set page config
st.set_page_config(page_title="Aniket AI DataInsight Pro", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
    }
    .stSelectbox>div>div {
        background-color: #ffffff;
    }
    h1, h2, h3 {
        color: #343a40;
    }
    .card {
        border-radius: 5px;
        box-shadow: 0 4px 6px 0 rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin: 10px 0;
        background-color: white;
    }
    .navbar {
        padding: 10px;
        background-color: #343a40;
        color: white;
    }
    .navbar a {
        color: white;
        text-decoration: none;
        padding: 10px;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #f2f2f2;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    
    .dataframe {
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 20px;
    }
    .dataframe th, .dataframe td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    .dataframe th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    .dataframe tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .dataframe tr:hover {
        background-color: #f5f5f5;
    }
    
</style>
""", unsafe_allow_html=True)

# Custom HTML for favicon
st.markdown("""
    <head>
        <link rel="icon" href="logo/logo.jpg" type="image/jpeg">
    </head>
""", unsafe_allow_html=True)

# Navbar
st.markdown("""
<div class="navbar">
    <a href="#">Home</a>
    <a href="#services">Services</a>
    <a href="#data-explorer">Data Explorer</a>
    <a href="#upload">Upload Dataset</a>
</div>
</br>
</br>
""", unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logo/logo.jpg", width=200)
st.title("Aniket AI DataInsight Pro")
st.write("Empowering Business Intelligence with Advanced Analytics Using AI")

# Services
st.markdown('<a name="services"></a>', unsafe_allow_html=True)
st.header("Our Services")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="card">
        <h3>Data Analysis</h3>
        <p>Unlock the power of your data with our advanced analytics tools.</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="card">
        <h3>Predictive Modeling</h3>
        <p>Forecast future trends and make data-driven decisions.</p>
    </div>
    """, unsafe_allow_html=True)

# Data Explorer Section
st.markdown('<a name="data-explorer"></a>', unsafe_allow_html=True)
st.header("Data Explorer")
table_names = get_table_names()
selected_table = st.selectbox("Select a dataset", table_names)

def format_df_to_html_table(df):
    return df.to_html(index=False, classes=['dataframe'], border=0)

if selected_table:
    db_path = os.path.join(DATABASE_FOLDER, f'{selected_table}.db')
    sqlite_connector = SqliteConnector(config={"database": db_path, "table": selected_table})
    df_connector = SmartDataframe(sqlite_connector, config={"llm": model})

    prompt = st.text_input("Ask a question about your data:")
    if st.button("Analyze"):
        if prompt:
            with st.spinner("Analyzing data..."):
                try:
                    response = df_connector.chat(prompt)

                    if isinstance(response, pd.DataFrame):
                        # Format the DataFrame into an HTML table
                        formatted_response = format_df_to_html_table(response)
                    else:
                        # If it's not a DataFrame, convert to string and wrap in a pre tag
                        formatted_response = f"<pre>{str(response)}</pre>"

                    # Display the formatted response
                    st.markdown(f'<div class="card">{formatted_response}</div>', unsafe_allow_html=True)

                    # Check if a chart was generated
                    chart_path = "exports/charts/temp_chart.png"
                    if os.path.exists(chart_path):
                        image = Image.open(chart_path)
                        st.image(image, caption="Generated Chart", use_column_width=True)
                        os.remove(chart_path)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a question about your data.")
else:
    st.info("No datasets available. Please upload a CSV file to begin analysis.")

# CSV Upload Section
st.markdown('<a name="upload"></a>', unsafe_allow_html=True)
st.header("Upload New Dataset")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    if st.button("Process Dataset"):
        df = pd.read_csv(uploaded_file)
        db_name = os.path.splitext(uploaded_file.name)[0]
        db_path = os.path.join(DATABASE_FOLDER, f'{db_name}.db')
        conn = sqlite3.connect(db_path)
        df.to_sql(db_name, conn, if_exists='replace', index=False)
        conn.close()
        st.success(f"Dataset '{uploaded_file.name}' has been processed and is ready for analysis.")
        st.experimental_rerun()

# Footer
st.markdown("---")
st.write("© 2024 Aniket AI DataInsight Pro. All rights reserved.")