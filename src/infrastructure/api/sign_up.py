import json
import boto3

from src.infrastructure.config.constants import COGNITO_APP_ID


def lambda_handler(event, context):
    client = boto3.client('cognito-idp')
    body = json.loads(event['body'])
    email = body['email']
    password = body['password']
    try:
        client.sign_up(
            ClientId=COGNITO_APP_ID,
            Username=email,
            Password=password,
        )
        # Retorna una confirmación de registro
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                'Access-Control-Allow-Methods': 'POST,OPTIONS,GET'
            },
            'body': json.dumps('User registration successful')
        }

    except client.exceptions.UsernameExistsException:
        return {
            'statusCode': 400,
            'body': json.dumps('User already exists')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Something went wrong: {str(e)}'),
        }
