# OCR Processing Service

This project provides an OCR API and minimal web interface. Documents are
processed using a Gemini based OCR service and the extracted fields are
returned as structured JSON.

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
document is sent to Gemini which extracts key/value pairs and returns them in a
JSON structure.  A small Flask application provides a basic HTML form to upload
documents and visualize the resulting fields.

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
| `GEMINI_API_KEY` | API key for Gemini OCR. |
| `GEMINI_MODEL` | Model name for Gemini OCR. |
| `OCR_SERVICE` | Which OCR backend to use: `gemini` or `textract`. |
| `AWS_REGION` | AWS region for Textract if using that backend. |
| `S3_BUCKET` | Temporary S3 bucket for PDF processing with Textract. |
| `DATABASE_URL` | Connection string for PostgreSQL. Defaults to the local container URL. |

## Running the stack

Start the services in detached mode:

```bash
docker-compose up --build -d
```

This will launch the following containers:

* **api** – FastAPI application exposing the OCR endpoint.
* **web** – Flask application for manual uploads.
* **db** – PostgreSQL database used for persistence.
* **db_viewer** – Web client for inspecting the database.

Access the API at `http://localhost:8000`, the web interface at
`http://localhost:5050` and the database viewer at
`http://localhost:8081`.

## API usage

Send a document to `/api/analyze` using `curl`:

```bash
curl -F "file=@path/to/document.pdf" http://localhost:8000/api/analyze
```

The response contains the detected form type, the original file name and a
dictionary of extracted fields:

```json
{
  "form_type": "text",
  "filename": "document.pdf",
  "fields": {
    "Nombre": "Juan"
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
tests/        # Unit tests for core functionality
docker-compose.yml
```

## Deployment

The `deploy.sh` script can be used to update a remote server that already has
the repository cloned. It pulls the latest changes and restarts the containers:

```bash
./deploy.sh
```
