# web/app.py
from flask import Flask, render_template, request
import requests
import logging

app = Flask(__name__, template_folder="templates")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.info("Starting Flask app...")

@app.route("/", methods=["GET", "POST"])
def index():
    logger.info("Received request: %s", request.method)
    # Si es una solicitud POST, procesar el archivo
    if request.method == "POST":
        file = request.files["document"]
        if file:
            response = requests.post("http://api:8000/api/analyze", files={"file": file})
            if response.ok:
                data = response.json()
                return render_template("index.html", fields=data.get("fields", {}))
            else:
                logger.error("Error en la API: %s %s", response.status_code, response.text)
                return render_template("index.html", fields={}, error="Error al procesar el documento.")

    logger.info("Rendering index.html")
    # Si es una solicitud GET, renderizar el formulario
    return render_template("index.html", fields={})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)