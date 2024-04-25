from flask import Flask, jsonify
import requests
import sqlite3

app = Flask(__name__)
DATABASE = "coordinates.db"

@app.route("/process_postcodes", methods=["GET"])
def process_postcodes():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, latitude, longitude FROM coordinates")
        coordinates = cursor.fetchall()

        postcodes = []
        for coord in coordinates:
            latitude, longitude = coord[1], coord[2]
            response = requests.get(f"https://api.postcodes.io/postcodes?lon={longitude}&lat={latitude}")
            data = response.json()

            if data["status"] == 200:
                postcode = data["result"]["postcode"]
                cursor.execute("UPDATE coordinates SET postcode = ? WHERE id = ?", (postcode, coord[0]))
                postcodes.append(postcode)
            else:
                return jsonify({"error": f"Error retrieving postcode for {latitude}, {longitude}"}), 400
        
        conn.commit()

    return jsonify({"postcodes": postcodes}), 200

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5002)
