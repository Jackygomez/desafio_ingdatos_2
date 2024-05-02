#manejará todas las interacciones con la base de datos

import os
import pyodbc
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Cargar variables de entorno
load_dotenv()

# Configuraciones de SQL Server
server = os.getenv('SQL_SERVER')
username = os.getenv('SQL_USERNAME')
password = os.getenv('SQL_PASSWORD')
database = "employeedirectorydb"

def connect_to_sql_server():
    cnxn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server={server},1433;Database={database};UID={username};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=220;"
    try:
        return pyodbc.connect(cnxn_str)
    except pyodbc.Error as e:
        logging.error(f"Failed to connect to SQL Server: {e}")
        raise

def fetch_coordinates():
    query = "SELECT id, latitude, longitude FROM coordinates"
    try:
        with connect_to_sql_server() as conn, conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    except pyodbc.Error as e:
        logging.error(f"Error fetching coordinates: {e}")
        raise

def update_postcode(id, postcode):
    query = "UPDATE coordinates SET postcode = ? WHERE id = ?"
    try:
        with connect_to_sql_server() as conn, conn.cursor() as cursor:
            cursor.execute(query, (postcode, id))
            conn.commit()
    except pyodbc.Error as e:
        logging.error(f"Error updating postcode: {e}")
        conn.rollback()
        raise


