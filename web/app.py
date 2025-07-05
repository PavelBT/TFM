# web/app.py
from flask import Flask, render_template, request, jsonify
import base64
import requests
from services.utils.logger import get_logger
from services.db_client import DatabaseClient

app = Flask(__name__, template_folder="templates", static_folder="static")
logger = get_logger(__name__)
logger.info("Starting Flask app...")
db_client = DatabaseClient()

VALID_FORMS = {"credito_personal", "credito_hipotecario", "credito_tarjeta"}

@app.route("/", methods=["GET", "POST"])
def index():
    logger.info("Received request: %s", request.method)
    # Si es una solicitud POST, procesar el archivo
    if request.method == "POST":
        file = request.files["document"]
        if file:
            try:
                file_bytes = file.read()
                files = {"file": (file.filename, file_bytes, file.mimetype)}
                response = requests.post("http://api:8000/api/analyze", files=files)
                if response.ok:
                    data = response.json()
                    form_type = data.get("form_type")
                    if form_type not in VALID_FORMS:
                        msg = (
                            "El formulario no es adecuado, "
                            "únicamente son válidos los formularios "
                            "Crédito personal, crédito hipotecario, "
                            "solicitud de tarjeta de crédito. "
                            f"Formulario subido identificado: {form_type}"
                        )
                        return render_template(
                            "index.html",
                            fields={},
                            error=msg,
                            file_url=None,
                            form_type=None,
                        )

                    b64_file = base64.b64encode(file_bytes).decode("utf-8")
                    file_url = f"data:{file.mimetype};base64,{b64_file}"
                    return render_template(
                        "index.html",
                        fields=data.get("fields", {}),
                        file_url=file_url,
                        is_pdf=file.mimetype == "application/pdf",
                        form_type=form_type,
                    )
                logger.error("Error en la API: %s %s", response.status_code, response.text)
                return render_template("index.html", fields={}, error="Error al procesar el documento.")
            except Exception as exc:
                logger.error("Fallo la solicitud a la API: %s", exc)
                return render_template("index.html", fields={}, error="Error al procesar el documento.")

    logger.info("Rendering index.html")
    # Si es una solicitud GET, renderizar el formulario
    return render_template("index.html", fields={}, file_url=None, form_type=None, error=None)


@app.route("/save", methods=["POST"])
def save():
    data = request.get_json() or {}
    form_type = data.get("form_type")
    fields = data.get("fields", {})
    file_url = data.get("file_url")
    try:
        db_client.save_form(form_type, fields, file_url)
        return jsonify({"status": "ok", "message": "Registro guardado correctamente"})
    except Exception as exc:  # pragma: no cover - just logging
        logger.error("Error saving form: %s", exc)
        return (
            jsonify({"status": "error", "message": "Error al guardar en la base de datos"}),
            500,
        )


@app.route("/applications", methods=["GET"])
def list_applications():
    """Display stored credit applications."""
    records = db_client.list_applications()
    return render_template("applications.html", records=records)


@app.route("/help", methods=["GET"])
def help_page():
    """Display user guide."""
    return render_template("help.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
