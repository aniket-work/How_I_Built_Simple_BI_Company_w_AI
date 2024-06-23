import streamlit as st
import os
import sqlite3
import pandas as pd
from pandasai import SmartDataframe

from pandasai.connectors import SqliteConnector
from langchain_groq.chat_models import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# Constants
DATABASE_FOLDER = 'database'
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Initialize GroqLLM
model = ChatGroq(
    model_name="mixtral-8x7b-32768",
    api_key = GROQ_API_KEY)


def get_table_names():
    table_names = []
    for file in os.listdir(DATABASE_FOLDER):
        if file.endswith('.db'):
            table_names.append(os.path.splitext(file)[0])
    return table_names


st.title("SQLite with Groq LLM")

# Table selection
table_names = get_table_names()
selected_table = st.selectbox("Select a table", table_names)

if selected_table:
    db_path = os.path.join(DATABASE_FOLDER, f'{selected_table}.db')

    # Create SQLite connector
    sqlite_connector = SqliteConnector(
        config={
            "database": db_path,
            "table": selected_table,
        }
    )

    # Create SmartDataframe
    df_connector = SmartDataframe(sqlite_connector, config={"llm": model})

    # User input
    prompt = st.text_input("Enter your prompt:")

    if st.button("Generate"):
        if prompt:
            with st.spinner("Generating response..."):
                try:
                    response = df_connector.chat(prompt)
                    st.write(response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a prompt.")
else:
    st.warning("No tables found. Please upload a CSV file first.")

# CSV Upload functionality
st.header("Upload CSV")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    if st.button("Process CSV"):
        # Read the CSV file
        df = pd.read_csv(uploaded_file)

        # Create a new SQLite database with the name of the CSV file
        db_name = os.path.splitext(uploaded_file.name)[0]
        db_path = os.path.join(DATABASE_FOLDER, f'{db_name}.db')

        # Save the DataFrame to the SQLite database
        conn = sqlite3.connect(db_path)
        df.to_sql(db_name, conn, if_exists='replace', index=False)
        conn.close()

        st.success(f"CSV file '{uploaded_file.name}' has been processed and saved to the database.")
        st.experimental_rerun()  # Rerun the app to update the table list

