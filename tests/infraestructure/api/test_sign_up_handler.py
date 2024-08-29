import json
import pytest
from unittest.mock import patch, MagicMock
from src.infrastructure.api.sign_up import lambda_handler

@pytest.mark.parametrize(
    "event, expected_status_code, expected_body, exception, test_id",
    [
        # Happy path tests
        (
                {'email': 'test@example.com', 'password': 'Password123!'},
                200,
                json.dumps('User registration successful'),
                None,
                "happy_path_1"
        ),
        (
                {'email': 'user2@example.com', 'password': 'Password456!'},
                200,
                json.dumps('User registration successful'),
                None,
                "happy_path_2"
        ),
        # Edge cases
        (
                {'email': 'user@example.com', 'password': 'short'},
                200,
                json.dumps('User registration successful'),
                None,
                "edge_case_short_password"
        ),
        (
                {'email': 'user@example.com', 'password': 'a'*129},
                200,
                json.dumps('User registration successful'),
                None,
                "edge_case_long_password"
        ),
        # Error cases
        (
                {'email': 'existinguser@example.com', 'password': 'Password123!'},
                400,
                json.dumps('User already exists'),
                'UsernameExistsException',
                "error_case_user_exists"
        ),
        (
                {'email': 'user@example.com', 'password': 'Password123!'},
                500,
                json.dumps('Something went wrong: An error occurred'),
                Exception('An error occurred'),
                "error_case_generic_exception"
        ),
    ],
    ids=lambda param: param[-1]  # Use the last element as the test ID
)
@patch('boto3.client')
def test_lambda_handler(mock_boto_client, event, expected_status_code, expected_body, exception, test_id):
    # Arrange
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client

    if exception == 'UsernameExistsException':
        mock_client.sign_up.side_effect = mock_client.exceptions.UsernameExistsException
    elif exception:
        mock_client.sign_up.side_effect = exception
    else:
        mock_client.sign_up.return_value = {'UserConfirmed': True}

    # Act
    response = lambda_handler(event, None)

    # Assert
    assert response['statusCode'] == expected_status_code
    assert response['body'] == expected_body
