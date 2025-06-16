from unittest.mock import MagicMock, patch
import sys


sys.modules.setdefault('boto3', MagicMock())
from services.ocr.textract.s3_uploader import S3Uploader


def test_s3_uploader_calls():
    with patch('boto3.client') as client_factory:
        mock_client = MagicMock()
        client_factory.return_value = mock_client
        uploader = S3Uploader('bucket', region_name='us-east-2')
        uploader.upload('key', b'data')
        uploader.delete('key')
        mock_client.put_object.assert_called_with(Bucket='bucket', Key='key', Body=b'data')
        mock_client.delete_object.assert_called_with(Bucket='bucket', Key='key')
