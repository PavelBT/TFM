# OCR Processing Service

This project provides an OCR API and minimal web interface. Documents are
processed using an OCR backend (AWS Textract by default) and the extracted
fields are optionally refined using AI models. A set of cleaners normalises the
data to return a structured JSON response.

The provided `ai_models` service hosts all AI models. It performs a first pass
with a lightweight mT5 model
(`dreuxx26/Multilingual-grammar-Corrector-using-mT5-small`) to fix common
errors and then sends the text to ChatGPT for a final correction. The API
container simply calls this service to refine OCR results.

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
| `AI_MODELS_URL` | Base URL for the `ai_models` service. |
| `AWS_ACCESS_KEY_ID` | AWS credential for Textract/S3. |
| `AWS_SECRET_ACCESS_KEY` | AWS credential for Textract/S3. |
| `AWS_REGION` | AWS region used by Textract. |
| `AWS_BUCKET` | S3 bucket for temporary uploads. |
| `OPENAI_API_KEY` | API key used by the `ai_models` service. |
| `OPENAI_MODEL` | ChatGPT model name. |
| `HF_MODEL_NAME` | Name of the local grammar model. |

## Usage

Upload a PDF or image via the `/api/analyze` endpoint or through the web
interface. The API returns a JSON payload with the detected form type, the
uploaded file name and the processed fields.
