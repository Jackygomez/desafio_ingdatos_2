#Manejará la lógica de procesamiento del archivo CSV
import csv
from data_access import init_db, store_csv_async
from threading import Thread
import logging

def process_csv_file(file):
    """
    Procesa el archivo CSV en un hilo separado para no bloquear la respuesta del servidor.
    Devuelve inmediatamente una respuesta al cliente indicando que el procesamiento ha comenzado.
    """
    try:
        file_text = file.stream.read().decode("utf-8")
        #csv_reader = csv.reader(file_text.splitlines(), delimiter='|', quotechar="'")
        csv_reader = csv_reader((line.split('|')[:3] for line in file_text.splitlines()))
        next(csv_reader, None)  # Omitir la cabecera

        thread = Thread(target=store_csv_async, args=(csv_reader,))
        thread.start()
        # No esperamos a que el hilo termine, el procesamiento continúa en el fondo.
        return "File is being processed", 202
    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        return "Failed to process file", 500

def initialize_database():
    """Inicializa la base de datos asegurándose que está lista antes de procesar cualquier archivo."""
    init_db()

if __name__ == "__main__":
    initialize_database()  # Asegura que la DB esté lista antes de aceptar archivos.
