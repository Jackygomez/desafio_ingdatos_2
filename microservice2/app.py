import os
from flask import Flask, jsonify
import pyodbc
import requests
from dotenv import load_dotenv

app = Flask(__name__)

# Cargar variables de entorno
load_dotenv()

# Configuraciones de SQL Server
server = os.getenv('SQL_SERVER')
username = os.getenv('SQL_USERNAME')
password = os.getenv('SQL_PASSWORD')
database = "employeedirectorydb"

# Conexión a SQL Server
def connect_to_sql_server():
    cnxn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={server},1433;Database={database};UID={username};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=220;"
    return pyodbc.connect(cnxn_str)

@app.route("/process_postcodes", methods=["GET"])
def process_postcodes():
    with connect_to_sql_server() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, latitude, longitude FROM coordinates")
        coordinates = cursor.fetchall()

        postcodes = []
        errors = []
        for coord in coordinates:
            latitude, longitude = coord[1], coord[2]
            try:
                response = requests.get(f"https://api.postcodes.io/postcodes?lon={longitude}&lat={latitude}")
                if response.status_code == 200:
                    data = response.json()
                    if data['result'] is not None:
                        postcode = data['result'][0]['postcode']
                        cursor.execute("UPDATE coordinates SET postcode = ? WHERE id = ?", (postcode, coord[0]))
                        postcodes.append(postcode)
                    else:
                        errors.append(f"No postcode found for coordinates ({latitude}, {longitude}).")
                else:
                    errors.append(f"API request failed for coordinates ({latitude}, {longitude}) with status code {response.status_code}.")
            except Exception as e:
                errors.append(f"Error processing coordinates ({latitude}, {longitude}): {str(e)}")

        conn.commit()
        if errors:
            return jsonify({"errors": errors}), 400
        return jsonify({"postcodes": postcodes}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)

