import json
import boto3

from src.infrastructure.config.constants import COGNITO_APP_ID


def lambda_handler(event, context):
    client = boto3.client('cognito-idp')

    try:
        body = json.loads(event['body'])
        email = body['email']
        confirmation_code = body['confirmation_code']
        response = client.confirm_sign_up(
            ClientId=COGNITO_APP_ID,
            Username=email,
            ConfirmationCode=confirmation_code
        )

        # Retorna una confirmación de éxito
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                'Access-Control-Allow-Methods': 'POST,OPTIONS,GET'
            },
            'body': json.dumps('User confirmation successful')
        }

    except client.exceptions.UserNotFoundException:
        return {
            'statusCode': 404,
            'body': json.dumps('User not found')
        }
    except client.exceptions.CodeMismatchException:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid confirmation code')
        }
    except client.exceptions.ExpiredCodeException:
        return {
            'statusCode': 400,
            'body': json.dumps('Confirmation code has expired')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Something went wrong: {str(e)}')
        }
