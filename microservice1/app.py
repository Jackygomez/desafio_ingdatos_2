import os
from flask import Flask, request, jsonify
import pyodbc
import csv
from dotenv import load_dotenv
from threading import Thread
import logging

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Cargar variables de entorno
load_dotenv()

# Configuraciones de SQL Server
server = os.getenv('SQL_SERVER')
username = os.getenv('SQL_USERNAME')
password = os.getenv('SQL_PASSWORD')
database = "employeedirectorydb"

# Conexión a SQL Server
def connect_to_sql_server():
    cnxn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={server},1433;Database={database};UID={username};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    return pyodbc.connect(cnxn_str)

def safe_float(value):
    # Eliminar comillas dobles y convertir comas en puntos
    cleaned_value = value.strip().replace("''", "").replace(",", ".")
    if cleaned_value.lower() == 'nan':
        return 0.0  # Trata 'nan' como 0
    try:
        return float(cleaned_value)
    except ValueError:
        return None  # Retorna None para cualquier otro valor no convertible

# Inicializa la base de datos y crea la tabla si no existe
def init_db():
    with connect_to_sql_server() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'coordinates')
            CREATE TABLE coordinates (
                id INT PRIMARY KEY IDENTITY(1,1),
                latitude FLOAT,
                longitude FLOAT
            )
            """
        )
        conn.commit()

# Almacenamiento asíncrono para mejorar el rendimiento
def store_csv_async(csv_reader):
    try:
        with connect_to_sql_server() as conn:
            cursor = conn.cursor()
            conn.autocommit = False
            valid_rows = 0
            for row in csv_reader:
                if row:
                    latitude_str, longitude_str = row[0].strip(), row[1].strip()
                    latitude = safe_float(latitude_str)
                    longitude = safe_float(longitude_str)
                    if latitude is not None and longitude is not None:
                        cursor.execute(
                            "INSERT INTO coordinates (latitude, longitude) VALUES (?, ?)", (latitude, longitude)
                        )
                        valid_rows += 1
            if valid_rows > 0:
                conn.commit()
                logging.info(f"Committed {valid_rows} rows to the database.")
            else:
                conn.rollback()
                logging.warning("No valid rows to insert, transaction rolled back.")
    except Exception as e:
        logging.error("Failed to process CSV: ", exc_info=True)

@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400
    
    file_text = file.stream.read().decode("utf-8")
    csv_reader = csv.reader(file_text.splitlines(), delimiter='|', quotechar="'")
    next(csv_reader, None)  # Omitir la cabecera
    
    thread = Thread(target=store_csv_async, args=(csv_reader,))
    thread.start()
    thread.join()  # Esperar a que el hilo termine para depuración
    
    return jsonify({"message": "File is being processed"}), 202

if __name__ == "__main__":
    init_db() 
    app.run(host="0.0.0.0", port=5001)
