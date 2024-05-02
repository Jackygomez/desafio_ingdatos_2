#Manejará todas las interacciones con la base de datos

import os
import pyodbc
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuraciones de SQL Server
server = os.getenv('SQL_SERVER')
username = os.getenv('SQL_USERNAME')
password = os.getenv('SQL_PASSWORD')
database = "employeedirectorydb"

def connect_to_sql_server():
    cnxn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={server},1433;Database={database};UID={username};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    return pyodbc.connect(cnxn_str)

def safe_float(value):
    cleaned_value = value.strip().replace("''", "").replace(",", ".")
    return float(cleaned_value) if cleaned_value.lower() != 'nan' else 0.0

# Configura el logging al nivel DEBUG para capturar todos los mensajes
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def store_csv_async(csv_reader):
    try:
        with connect_to_sql_server() as conn, conn.cursor() as cursor:
            conn.autocommit = False
            valid_rows = sum(1 for row in csv_reader if process_row(cursor, row))
            if valid_rows > 0:
                conn.commit()
                logging.info(f"Committed {valid_rows} rows to the database.")
            else:
                conn.rollback()
                logging.warning("No valid rows to insert, transaction rolled back.")
    except pyodbc.DatabaseError as e:
        logging.error("Database error: %s", str(e), exc_info=True)
    except Exception as e:
        logging.error("Failed to process CSV: %s", str(e), exc_info=True)

def process_row(cursor, row):
    latitude, longitude = (safe_float(val) for val in row)
    if latitude is not None and longitude is not None:
        cursor.execute("INSERT INTO coordinates (latitude, longitude) VALUES (?, ?)", (latitude, longitude))
        return True
    return False

def init_db():
    with connect_to_sql_server() as conn, conn.cursor() as cursor:
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