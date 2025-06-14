# OCR Form Processor

Este proyecto ofrece una API construida con FastAPI y una interfaz web con Flask para procesar formularios escaneados. Utiliza Amazon Textract para la extracción OCR y diferentes refinadores basados en IA para mejorar los resultados.

## Instalación

1. Clonar el repositorio.
2. Crear un entorno virtual y activar.
3. Instalar dependencias:

```bash
pip install -r app/requirements.txt
```

## Variables de entorno

- `OCR_SERVICE`: Nombre del servicio OCR a usar (`aws` por defecto).
- `REFINER_TYPE`: Tipo de refinador IA (`gpt` o `huggingface`).
- `OPENAI_API_KEY`: Clave de OpenAI cuando se usa el refinador GPT.

## Uso

Iniciar la API:

```bash
uvicorn api.main:app --reload
```

Iniciar la interfaz web:

```bash
python web/app.py
```

Luego abrir `http://localhost:5000` en el navegador para cargar un documento.


### Mejoras recientes
- Los nombres de campo conservan los delimitadores "/" convirtiéndolos en "_".
- El OCR de Textract agrupa las líneas manuscritas por secciones del formulario
  Banorte utilizando los encabezados impresos (información del crédito,
  información personal, domicilio, empleo y referencias personales).
