# OCR Processing Service

This project provides an OCR API and minimal web interface. Documents are
processed using an OCR backend (AWS Textract by default) and the extracted
fields are optionally refined using AI models. A set of cleaners normalises the
data to return a structured JSON response.

## Installation

1. Clone this repository.
2. Copy `.env.example` to `.env` and fill in your credentials.
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

## Usage

Upload a PDF or image via the `/api/analyze` endpoint or through the web
interface. The API returns a JSON payload with the detected form type, the
uploaded file name and the processed fields.
