import os
from flask import Flask, request, jsonify
import pyodbc
import csv
from dotenv import load_dotenv
from threading import Thread

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

# Almacenamiento asíncrono para mejorar el rendimiento
def store_csv_async(csv_reader):
    with connect_to_sql_server() as conn:
        cursor = conn.cursor()
        conn.autocommit = False  # Uso de transacciones
        try:
            for row in csv_reader:
                latitude_str, longitude_str = row
                latitude = safe_float(latitude_str)
                longitude = safe_float(longitude_str)

                if latitude is not None and longitude is not None:
                    cursor.execute(
                        "INSERT INTO coordinates (latitude, longitude) VALUES (?, ?)", (latitude, longitude)
                    )
            conn.commit()  # Confirmar transacción
        except Exception as e:
            conn.rollback()  # Revertir en caso de error
            raise e  # Re-lanzar el error

# Endpoint para subir el archivo CSV
@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400
    
    file_text = file.stream.read().decode("utf-8")
    csv_reader = csv.reader(file_text.splitlines(), delimiter='|', quotechar="'")

    # Omitir la primera línea si es cabecera
    next(csv_reader, None)

    # Almacenamiento asíncrono para reducir el tiempo de respuesta
    thread = Thread(target=store_csv_async, args=(csv_reader,))
    thread.start() 
    
    return jsonify({"message": "File is being processed"}), 202 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
