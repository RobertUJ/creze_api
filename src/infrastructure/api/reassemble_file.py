import json
import boto3

from src.infrastructure.config import S3_BUCKET_NAME

s3_client = boto3.client('s3')
BUCKET_NAME = S3_BUCKET_NAME


def lambda_handler(event, context):
    try:
        # 1. Parse the data from the event payload
        file_name = event['file_name']
        total_parts = event['total_chunks']

        assembled_content = b''

        # 2. download and concatenate all the parts
        for i in range(total_parts):
            chunk_key = f"{file_name}/chunk_{i}"
            print(chunk_key)
            part = s3_client.get_object(Bucket=BUCKET_NAME, Key=chunk_key)
            assembled_content += part['Body'].read()

        # 3. upload the assembled file
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=f'assembled/{file_name}',
            Body=assembled_content
        )

        # 4. Clean up the chunks after reassembling
        for i in range(total_parts):
            chunk_key = f"{file_name}/chunk_{i}"
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=chunk_key)

        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                'Access-Control-Allow-Methods': 'POST,OPTIONS,GET'
            },
            'body': json.dumps({'message': 'File reassembled successfully', 'file_name': file_name})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                'Access-Control-Allow-Methods': 'POST,OPTIONS,GET'
            },
            'body': json.dumps({'message': str(e)})
        }