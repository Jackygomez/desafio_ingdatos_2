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
    cnxn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={server},1433;Database={database};UID={username};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    return pyodbc.connect(cnxn_str)

# Función para convertir a flotante de forma segura
def safe_float(value):
    try:
        # Remover comillas simples y convertir comas en puntos para manejar decimales
        cleaned_value = value.replace("''", "").replace(",", ".")
        return float(cleaned_value)
    except ValueError:
        return None

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
    with connect_to_sql_server() as conn:
        cursor = conn.cursor()
        conn.autocommit = False
        valid_rows = 0
        for row in csv_reader:
            latitude, longitude = row
            latitude = safe_float(latitude)
            longitude = safe_float(longitude)
            if latitude is not None and longitude is not None:
                cursor.execute(
                    "INSERT INTO coordinates (latitude, longitude) VALUES (?, ?)", (latitude, longitude)
                )
                valid_rows += 1
        if valid_rows > 0:
            conn.commit()
        else:
            conn.rollback()

@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400
    
    file_text = file.stream.read().decode("utf-8")
    csv_reader = csv.reader(file_text.splitlines(), delimiter='|', quotechar="'")
    next(csv_reader)  # Omitir la cabecera
    
    thread = Thread(target=store_csv_async, args=(csv_reader,))
    thread.start()
    thread.join()  # Asegurar que el proceso termine para fines de prueba
    
    return jsonify({"message": "File is being processed"}), 202

if __name__ == "__main__":
    init_db() 
    app.run(host="0.0.0.0", port=5001)
