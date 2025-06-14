# web/app.py
from flask import Flask, render_template, request
import logging
import requests

app = Flask(__name__, template_folder="templates")
logging.basicConfig(level=logging.INFO)
logging.info("Starting Flask app...")

@app.route("/", methods=["GET", "POST"])
def index():
    logging.info("Received request: %s", request.method)
    # Si es una solicitud POST, procesar el archivo
    if request.method == "POST":
        file = request.files["document"]
        if file:
            response = requests.post("http://api:8000/api/analyze", files={"file": file})
            if response.ok:
                data = response.json()
                return render_template("index.html", fields=data.get("fields", {}))
            else:
                logging.error("Error en la API: %s %s", response.status_code, response.text)
                return render_template("index.html", fields={}, error="Error al procesar el documento.")

    logging.info("Rendering index.html")
    # Si es una solicitud GET, renderizar el formulario
    return render_template("index.html", fields={})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
