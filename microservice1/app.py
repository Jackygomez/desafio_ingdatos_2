from flask import Flask, request, jsonify
import sqlite3
import csv

app = Flask(__name__)
DATABASE = "coordinates.db"

# Inicializa la base de datos
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS coordinates (id INTEGER PRIMARY KEY, latitude REAL, longitude REAL)"
        )
        conn.commit()

# Endpoint para subir el archivo CSV
@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        csv_reader = csv.reader(file.stream)
        for row in csv_reader:
            try:
                latitude, longitude = map(float, row)
                cursor.execute(
                    "INSERT INTO coordinates (latitude, longitude) VALUES (?, ?)", (latitude, longitude)
                )
            except Exception as e:
                return jsonify({"error": f"Error processing row {row}: {e}"}), 400
        conn.commit()

    return jsonify({"message": "File uploaded successfully"}), 200

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001)
