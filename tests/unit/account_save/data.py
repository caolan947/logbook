import boto3, os
from moto import mock_aws
from unittest.mock import Mock
from botocore.exceptions import ClientError
from tests.test_data import TestData

@mock_aws
class AccountSaveTestData(TestData):
    def __init__(self):
        super().__init__()

        self.fake_user_pool_name = "user_pool_name"
        self.fake_client_name = "client_name"
        self.fake_event = {
            "body": f"{{\"username\": \"{self.fake_username}\", \"password\": \"{self.fake_password}\"}}"
        }

        self.fake_client = boto3.client("cognito-idp", region_name=os.environ["region"])

        self.fake_user_pool_response = self.fake_client.create_user_pool(
            PoolName=self.fake_user_pool_name
        )

        self.fake_user_pool_client_response = self.fake_client.create_user_pool_client(
            UserPoolId=self.fake_user_pool_response["UserPool"]["Id"],
            ClientName=self.fake_client_name
        )
        
        self.fake_client_id = self.fake_user_pool_client_response["UserPoolClient"]["ClientId"]

        self.fake_sign_up_response = self.fake_client.sign_up(
            ClientId=self.fake_client_id,
            Username=self.fake_username,
            Password=self.fake_password
        )

        self.fake_unpacked_message = Mock(
            event=self.user_pw_body,
            message_body={
                "username": self.fake_username,
                "password": self.fake_password
        })

        self.fake_user_exists_exception = ClientError(
            operation_name="SignUp", 
            error_response={
                "Error": {
                    "Code": "UsernameExistsException", 
                    "Message": "An account with the given email already exists."
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