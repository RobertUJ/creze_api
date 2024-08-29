import boto3
import json

from src.infrastructure.config import S3_BUCKET_NAME

s3 = boto3.client('s3')
BUCKET_NAME = S3_BUCKET_NAME


def create_presigned_url(key: str, expiration: int = 3600):
    return s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': key},
        ExpiresIn=expiration
    )


def lambda_handler(event, context):
    # Obtener la lista de documentos en el bucket
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    documents = []

    # Si hay documentos, los procesa para crear una lista simplificada
    if 'Contents' in response:
        documents.extend(
            {
                'Key': item['Key'],
                'Size': item['Size'],
                'LastModified': item['LastModified'].strftime(
                    '%Y-%m-%d %H:%M:%S'
                ),
                'Url': create_presigned_url(item['Key'])
            }
            for item in response['Contents']
        )
    return {
        'statusCode': 200,
        'body': json.dumps({
            'documents': documents
        }),
        'headers': {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Methods": "POST,OPTIONS,GET"
        },
    }
