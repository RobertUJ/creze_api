import json
import uuid
import base64
from requests_toolbelt.multipart import decoder

import boto3
from src.infrastructure.config import S3_BUCKET_NAME

s3_client = boto3.client('s3')
BUCKET_NAME = S3_BUCKET_NAME  # Reemplaza con el nombre de tu bucket


def trigger_reassemble(file_name, total_chunks):
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
        FunctionName='creze-docs-api-dev-reassembleFile',
        InvocationType='Event',
        Payload=json.dumps(
            {'file_name': file_name, 'total_chunks': total_chunks}
        ),
    )

def lambda_handler(event, context):
    try:
        # 1. Parse the data from the event payload
        if is_base_64_encoded := event.get('isBase64Encoded', False):
            body = base64.b64decode(event.get('body'))
        else:
            body = event.get('body')
            if isinstance(body, str):
                body = body.encode('utf-8')

        print("body", body)

        # 2. Parse data from multipart/form-data and get/set params and get binary data
        headers = event.get('headers', {})
        content_type = headers.get('content-type') or headers.get('Content-Type')
        multipart_data = decoder.MultipartDecoder(body, content_type)

        print("content_type", content_type)
        print("headers", headers)
        print("Multipart", multipart_data.parts)

        file_name = None
        chunk_index = 1
        total_chunks = 1
        chunk_data = ''

        for part in multipart_data.parts:
            if part.headers[b'Content-Disposition'].decode().find('name="fileName"') != -1:
                file_name = part.text
            elif part.headers[b'Content-Disposition'].decode().find('name="index"') != -1:
                chunk_index = int(part.text)
            elif part.headers[b'Content-Disposition'].decode().find('name="totalChunks"') != -1:
                total_chunks = int(part.text)
            elif part.headers[b'Content-Disposition'].decode().find('name="chunk"') != -1:
                chunk_data = part.content

        print("file_name", file_name)
        print("chunk_index", chunk_index)
        print("total_chunks", total_chunks)
        print("chunk_data", chunk_data)

        # 3. temporary file name and store the chunk to S3
        chunk_key = f"{file_name}/chunk_{chunk_index}"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=chunk_key,
            Body=chunk_data
        )
        # 4. if is this the last chunk, them call the reassemble lambda
        if chunk_index == total_chunks - 1:
            trigger_reassemble(file_name, total_chunks)
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'POST,OPTIONS,GET',
                'Content-Type': 'application/octet-stream'
            },
            'body': (
                json.dumps({'message': 'File uploaded successfully', 'file_name': 'file_name'})
            )
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'POST,OPTIONS,GET',
                'Content-Type': 'application/octet-stream'
            },
            'body': json.dumps({'message': str(e)})
        }
