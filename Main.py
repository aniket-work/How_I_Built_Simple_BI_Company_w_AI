import streamlit as st
import os
import sqlite3
import pandas as pd
from pandasai import SmartDataframe
from pandasai.connectors import SqliteConnector
from langchain_groq.chat_models import ChatGroq
from dotenv import load_dotenv

# Load environment variables and set constants
load_dotenv()
DATABASE_FOLDER = 'database'
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Initialize GroqLLM
model = ChatGroq(model_name="mixtral-8x7b-32768", api_key=GROQ_API_KEY)

# Function to get table names
def get_table_names():
    return [os.path.splitext(file)[0] for file in os.listdir(DATABASE_FOLDER) if file.endswith('.db')]

# Set page config
st.set_page_config(page_title="DataInsight Pro", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #0066cc;
        color: white;
    }
    .stSelectbox>div>div {
        background-color: #ffffff;
    }
    h1, h2, h3 {
        color: #003366;
    }
</style>
""", unsafe_allow_html=True)

# Custom HTML for favicon (replace URL with your actual icon URL)
st.markdown("""
    <head>
        <link rel="icon" href="logo/logo.jpg" type="image/x-icon">
    </head>
""", unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logo/logo.jpg", width=300)  # Replace with your logo
st.title("Aniket AI DataInsight Pro")
st.write("Empowering Business Intelligence with Advanced Analytics Using AI")

# Main content
st.header("Our Services")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Data Analysis")
    st.write("Unlock the power of your data with our advanced analytics tools.")
with col2:
    st.subheader("Predictive Modeling")
    st.write("Forecast future trends and make data-driven decisions.")

# Data Explorer Section
st.header("Data Explorer")
table_names = get_table_names()
selected_table = st.selectbox("Select a dataset", table_names)

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
                    st.write(response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a question about your data.")
else:
    st.info("No datasets available. Please upload a CSV file to begin analysis.")

# CSV Upload Section
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
st.write("© 2024 DataInsight Pro. All rights reserved.")