import os
import csv
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

DATABASE_FOLDER = 'database'
if not os.path.exists(DATABASE_FOLDER):
    os.makedirs(DATABASE_FOLDER)


def create_table_from_csv(csv_file, table_name):
    conn = sqlite3.connect(os.path.join(DATABASE_FOLDER, f'{table_name}.db'))
    cursor = conn.cursor()

    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)

        # Create table
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{header} TEXT' for header in headers])})"
        cursor.execute(create_table_query)

        # Insert data
        insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['?' for _ in headers])})"
        cursor.executemany(insert_query, csv_reader)

    conn.commit()
    conn.close()


@app.route('/process_client_onboard', methods=['POST'])
def process_client_onboard():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        filename = file.filename
        table_name = os.path.splitext(filename)[0]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        create_table_from_csv(file_path, table_name)

        return jsonify({"message": f"Table '{table_name}' created successfully"}), 200
    else:
        return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400


@app.route('/synch_up_data', methods=['POST'])
def synch_up_data():
    data = request.json
    if not data or 'table_name' not in data or 'records' not in data:
        return jsonify({"error": "Invalid data format"}), 400

    table_name = data['table_name']
    records = data['records']

    conn = sqlite3.connect(os.path.join(DATABASE_FOLDER, f'{table_name}.db'))
    cursor = conn.cursor()

    try:
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]

        # Prepare the insert or replace query
        placeholders = ', '.join(['?' for _ in columns])
        query = f"INSERT OR REPLACE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

        # Execute the query for each record
        for record in records:
            values = [record.get(col, None) for col in columns]
            cursor.execute(query, values)

        conn.commit()
        return jsonify({"message": f"Data synchronized successfully for table '{table_name}'"}), 200

    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    finally:
        conn.close()


if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = 'uploads'
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)