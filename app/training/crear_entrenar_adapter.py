
import logging
import boto3

# Configura tu bucket y archivo
bucket_name = "mi-bucket"  # Reemplaza con tu bucket real
dataset_path = "textract-adapters/textract_adapter_dataset.jsonl"
output_adapter_name = "adaptador-solicitud-credito"
role_arn = "arn:aws:iam::123456789012:role/TextractAdapterRole"  # Reemplaza con tu IAM Role

logging.basicConfig(level=logging.INFO)
textract = boto3.client("textract")

# Paso 1: Crear el adapter
response = textract.create_adapter(
    Name=output_adapter_name,
    Description="Adapter personalizado para solicitud de crédito personal"
)
adapter_id = response["AdapterId"]
logging.info("Adapter creado con ID: %s", adapter_id)

# Paso 2: Iniciar el entrenamiento
train_response = textract.start_adapter_training(
    AdapterId=adapter_id,
    FeatureType="QUERIES",
    TrainingConfig={
        "Documents": {
            "S3Bucket": bucket_name,
            "S3Prefix": dataset_path
        },
        "GroundTruthDataFormat": "APPLICATION_V2"
    },
    OutputConfig={
        "S3OutputPath": f"s3://{bucket_name}/textract-adapters/output/"
    },
    RoleArn=role_arn
)

logging.info("Entrenamiento iniciado. JobId: %s", train_response["JobId"])

