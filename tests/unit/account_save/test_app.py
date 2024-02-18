import unittest
from unittest.mock import patch, Mock
import boto3
from moto import mock_aws
import os

os.environ['account_user_pool_client'] = 'fake_id'

from account_save import app
from botocore.exceptions import ClientError
from aws_lambda_context import LambdaContext

class TestAccountSaveApp(unittest.TestCase):

    @mock_aws
    def setUp(self):
        self.fake_username = "username"
        self.fake_password = "Password123!"
        self.fake_user_pool_name = "user_pool_name"
        self.fake_client_name = "client_name"
        self.fake_event = {
            "body": f"{{\"username\": \"{self.fake_username}\", \"password\": \"{self.fake_password}\"}}"
        }
        self.fake_context = LambdaContext()

        self.loaded_body = {"username": self.fake_username, "password": self.fake_password}

        self.fake_client = boto3.client("cognito-idp", region_name="eu-west-1")

        self.fake_user_pool_response = self.fake_client.create_user_pool(
            PoolName=self.fake_user_pool_name
        )

        self.fake_user_pool_client_response = self.fake_client.create_user_pool_client(
            UserPoolId=self.fake_user_pool_response['UserPool']['Id'],
            ClientName=self.fake_client_name
        )
        
        self.fake_client_id = self.fake_user_pool_client_response['UserPoolClient']['ClientId']

        self.fake_sign_up_response = self.fake_client.sign_up(
            ClientId=self.fake_client_id,
            Username=self.fake_username,
            Password=self.fake_password
        )

        self.fake_unpacked_message = Mock(
            event=self.loaded_body,
            message_body={
                'username': self.fake_username,
                'password': self.fake_password
            })
        
        self.fake_exception = ClientError(
            operation_name='Test', 
            error_response={
                'Error': {
                    'Code': 'SomeError', 
                    'Message': 'This is an error'
                }
            }
        )

        self.fake_user_exists_exception = ClientError(
            operation_name='SignUp', 
            error_response={
                'Error': {
                    'Code': 'UsernameExistsException', 
                    'Message': 'An account with the given email already exists.'
                }
            }
        )

        self.fake_cognito_sign_up_error_false = {
            "error": False,
            "message": f"Successfully signed up new user {self.fake_username} in Cognito user pool {self.fake_client_id} and got response {self.fake_sign_up_response}",
            "data": self.fake_sign_up_response
        }

        self.fake_cognito_sign_up_error_true_generic = {
            "error": True,
            "message": f"An unexpected error occurred when creating user {self.fake_username} in Cognito user pool {self.fake_client_id} and raised exception {repr(self.fake_exception)}",
            "data": self.fake_exception
        }

        self.fake_cognito_sign_up_error_true_user_exists = {
            "error": True,
            "message": f"An account with the given email already exists.",
            "data": self.fake_user_exists_exception
        }

    @patch('account_save.app.Response')
    @patch.object(app, 'cognito_sign_up')
    @patch('account_save.app.UnpackSqsMessage')
    def test_lambda_handler(self, mock_unpacked_unpacked_message, mock_res, mock_Response):
        mock_unpacked_unpacked_message.return_value = self.fake_unpacked_message
        mock_res.return_value = self.fake_cognito_sign_up_error_false
        mock_Response.return_value.to_json.return_value = {
            'statusCode': 200,
            'body': self.fake_cognito_sign_up_error_false
        } 

        expected_result = {
            'statusCode': 200,
            'body': self.fake_cognito_sign_up_error_false
        }
        actual_result = app.lambda_handler(self.fake_event, self.fake_context)
        
        with self.subTest():
            self.assertEqual(expected_result, actual_result)

        mock_res.return_value = self.fake_cognito_sign_up_error_true_user_exists
        mock_Response.return_value.to_json.return_value = {
            'statusCode': 500,
            'body': self.fake_cognito_sign_up_error_true_user_exists
        }

        expected_result = {
            'statusCode': 500,
            'body': self.fake_cognito_sign_up_error_true_user_exists
        }
        actual_result = app.lambda_handler(self.fake_event, self.fake_context)
        
        with self.subTest():
            self.assertEqual(expected_result, actual_result)
    
    @patch('account_save.app.client')
    def test_cognito_sign_up(self, mock_client):
        mock_client.sign_up.return_value = self.fake_sign_up_response

        expected_result = self.fake_cognito_sign_up_error_false
        actual_result = app.cognito_sign_up(self.fake_client_id, self.loaded_body["username"], self.loaded_body["password"])

        with self.subTest():
            self.assertEqual(expected_result, actual_result)

        mock_client.sign_up.side_effect = self.fake_exception

        expected_result = self.fake_cognito_sign_up_error_true_generic
        actual_result = app.cognito_sign_up(self.fake_client_id, self.loaded_body["username"], self.loaded_body["password"])

        with self.subTest():
            self.assertEqual(expected_result, actual_result)

        mock_client.sign_up.side_effect = self.fake_user_exists_exception

        expected_result = self.fake_cognito_sign_up_error_true_user_exists
        actual_result = app.cognito_sign_up(self.fake_client_id, self.loaded_body["username"], self.loaded_body["password"])

        with self.subTest():
            self.assertEqual(expected_result, actual_result)