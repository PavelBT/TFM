# OCR Processing Service

This project provides an OCR API and minimal web interface. Documents are
processed using an OCR backend (AWS Textract by default) and the extracted
fields are optionally refined using AI models. A set of cleaners normalises the
data to return a structured JSON response.

## Table of Contents

1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Environment variables](#environment-variables)
5. [Running the stack](#running-the-stack)
6. [API usage](#api-usage)
7. [Web interface](#web-interface)
8. [Testing](#testing)
9. [Project layout](#project-layout)
10. [Deployment](#deployment)

## Overview

The service exposes a FastAPI endpoint that accepts PDF or image files.  Each
document is sent to an OCR backend which extracts the key/value pairs.  The
fields are cleaned, optionally sent through an AI model for further refinement
and returned as structured JSON.  A small Flask application provides a basic
HTML form to upload documents and visualize the resulting fields.

Supported OCR providers and refiners can be configured through environment
variables.  By default the stack relies on AWS Textract and does not apply AI
refinement.

## Requirements

* Docker and Docker Compose
* (Optional) Python 3.11+ if you wish to run the apps locally

## Installation

1. Clone this repository.
2. Copy `.env.example` to `.env` and adjust the values as needed.
3. Build and start the containers:

   ```bash
   docker-compose up --build
   ```

   The API will be available at `http://localhost:8000` and the web interface at
   `http://localhost:5050`.

## Environment variables

| Variable | Description |
| -------- | ----------- |
| `OCR_SERVICE` | Name of the OCR backend (`aws` by default). |
| `REFINER_TYPE` | Optional AI refiner (`gpt` or `huggingface`). |
| `AWS_ACCESS_KEY_ID` | AWS credential for Textract/S3. |
| `AWS_SECRET_ACCESS_KEY` | AWS credential for Textract/S3. |
| `AWS_REGION` | AWS region used by Textract. |
| `AWS_BUCKET` | S3 bucket for temporary uploads. |
| `OPENAI_API_KEY` | API key for GPT refiner (if used). |
| `OPENAI_MODEL` | Model name for GPT refiner. |
| `HF_MODEL_NAME` | Model name for HuggingFace refiner. |
| `TEXTRACT_MAX_RETRIES` | Maximum polling attempts for Textract jobs. |
| `TEXTRACT_SLEEP_SECONDS` | Delay between Textract polling attempts. |

## Running the stack

Start the services in detached mode:

```bash
docker-compose up --build -d
```

This will launch the following containers:

* **api** – FastAPI application exposing the OCR endpoint.
* **web** – Flask application for manual uploads.
* **db** – PostgreSQL database used for persistence.

Access the API at `http://localhost:8000` and the web interface at
`http://localhost:5050`.

## API usage

Send a document to `/api/analyze` using `curl`:

```bash
curl -F "file=@path/to/document.pdf" http://localhost:8000/api/analyze
```

The response contains the detected form type, the original file name and a
dictionary of cleaned fields:

```json
{
  "form_type": "banorte_credito",
  "filename": "document.pdf",
  "fields": {
    "datos_personales": {"nombre": "Juan"},
    "contacto": {"email": "test@mail.com"}
  }
}
```

### Web interface

Navigate to `http://localhost:5050` and upload a file using the provided form.
Detected fields will be rendered in a simple HTML view.

## Testing

Execute the test suite with `pytest`:

```bash
pytest -q
```

## Project layout

```
app/          # FastAPI service and OCR processing logic
web/          # Flask UI to upload files
ai_models/    # Optional HuggingFace-based refiner service
tests/        # Unit tests for core functionality
docker-compose.yml
```

## Deployment

The `deploy.sh` script can be used to update a remote server that already has
the repository cloned. It pulls the latest changes and restarts the containers:

```bash
./deploy.sh
```
