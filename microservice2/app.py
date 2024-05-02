#manejar las rutas y las respuestas HTTP

from flask import Flask, jsonify
from postcode_logic import get_and_update_postcodes
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

@app.route("/process_postcodes", methods=["GET"])
def process_postcodes():
    """
    Endpoint para procesar y actualizar códigos postales de coordenadas almacenadas.
    Devuelve una lista de códigos postales actualizados o errores si los hay.
    """
    try:
        postcodes, errors = get_and_update_postcodes()
        if errors:
            logging.error(f"Errors encountered while processing postcodes: {errors}")
            return jsonify({"errors": errors}), 400
        logging.info(f"Postcodes processed successfully: {postcodes}")
        return jsonify({"postcodes": postcodes}), 200
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
