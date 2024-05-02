#Manejar las rutas de Flask y las solicitudes de los usuarios

from flask import Flask, request, jsonify
from logic import process_csv_file
import logging

# Inicializa la aplicación Flask
app = Flask(__name__)

def configure_app():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    """
    Procesa la carga de un archivo CSV mediante una solicitud POST.
    Devuelve un mensaje de éxito o error dependiendo del resultado del procesamiento.
    """
    file = request.files.get("file")
    if not file:
        logging.error("No file provided")
        return jsonify({"error": "No file provided"}), 400

    try:
        message, status = process_csv_file(file)
        return jsonify({"message": message}), status
    except Exception as e:
        logging.error(f"Error processing the file: {str(e)}")
        return jsonify({"error": "Failed to process the file"}), 500

if __name__ == "__main__":
    configure_app()
    app.run(host="0.0.0.0", port=5001)
