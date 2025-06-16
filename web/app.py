# web/app.py
from flask import Flask, render_template, request
import requests
from services.utils.logger import get_logger

app = Flask(__name__, template_folder="templates")
logger = get_logger(__name__)
logger.info("Starting Flask app...")

@app.route("/", methods=["GET", "POST"])
def index():
    logger.info("Received request: %s", request.method)
    # Si es una solicitud POST, procesar el archivo
    if request.method == "POST":
        file = request.files["document"]
        if file:
            try:
                response = requests.post("http://api:8000/api/analyze", files={"file": file})
                if response.ok:
                    data = response.json()
                    return render_template("index.html", fields=data.get("fields", {}))
                logger.error("Error en la API: %s %s", response.status_code, response.text)
                return render_template("index.html", fields={}, error="Error al procesar el documento.")
            except Exception as exc:
                logger.error("Fallo la solicitud a la API: %s", exc)
                return render_template("index.html", fields={}, error="Error al procesar el documento.")

    logger.info("Rendering index.html")
    # Si es una solicitud GET, renderizar el formulario
    return render_template("index.html", fields={})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
