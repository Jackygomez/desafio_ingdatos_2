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

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_sql_server():
    cnxn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={server},1433;Database={database};UID={username};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    try:
        return pyodbc.connect(cnxn_str)
    except pyodbc.Error as e:
        logging.error(f"Failed to connect to SQL Server: {e}")
        raise ConnectionError(f"Failed to connect to SQL Server: {e}")

def safe_float(value):
    try:
        clean_value = value.strip("'")
        clean_value = clean_value.replace(",", ".")
        if clean_value.lower() == 'nan':
            return 0.0
        return float(clean_value)
    except ValueError as e:
        logging.error(f"Error converting {value} to float: {e}")
        return 0.0

def store_csv_async(csv_reader):
    try:
        with connect_to_sql_server() as conn:
            cursor = conn.cursor()
            conn.autocommit = False
            valid_rows = sum(1 for row in csv_reader if process_row(cursor, row))
            if valid_rows > 0:
                conn.commit()
                logging.info(f"Committed {valid_rows} rows to the database.")
            else:
                conn.rollback()
                logging.warning("No valid rows to insert, transaction rolled back.")
    except pyodbc.Error as e:
        conn.rollback()
        logging.error(f"Database operation failed: {e}", exc_info=True)
        raise

def process_row(cursor, row):
    latitude, longitude = (safe_float(val) for val in row)
    if latitude is not None and longitude is not None:
        cursor.execute("INSERT INTO coordinates (latitude, longitude) VALUES (?, ?)", (latitude, longitude))
        return True
    return False

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
            );
            """
        )
        conn.commit()
