import json
import boto3

from src.infrastructure.config.constants import COGNITO_APP_ID


def lambda_handler(event, context):
    client = boto3.client('cognito-idp')
    try:
        # 1. Parse the data from the event payload
        body = json.loads(event['body'])
        email = body.get('email')
        password = body.get('password')
        # 2. Authenticate the user with Cognito
        response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            },
            ClientId=COGNITO_APP_ID
        )
        # 3. Return the authentication tokens
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                'Access-Control-Allow-Methods': 'POST,OPTIONS,GET'
            },
            'body': json.dumps({
                'id_token': response['AuthenticationResult']['IdToken'],
                'access_token': response['AuthenticationResult']['AccessToken'],
                'refresh_token': response['AuthenticationResult']['RefreshToken'],
            })
        }

    except client.exceptions.NotAuthorizedException as e:
        return {
            'statusCode': 401,
            'body': json.dumps('Unauthorized')
        }
    except client.exceptions.UserNotFoundException as e:
        return {
            'statusCode': 404,
            'body': json.dumps('User not found')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Something went wrong: {str(e)}'),
        }
