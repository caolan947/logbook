from botocore.exceptions import ClientError
from aws_lambda_context import LambdaContext
import os
os.environ["region"] = "eu-west-1"

class TestData():
    def __init__(self):
        self.fake_context = LambdaContext()

        self.fake_exception = ClientError(
            operation_name="Test", 
            error_response={
                "Error": {
                    "Code": "SomeError", 
                    "Message": "This is an error"
                }
            }
        )

        self.fake_username = "fake_username@email.com"
        self.fake_password = "Fake_Password123!"
        self.user_pw_body = {"username": self.fake_username, "password": self.fake_password}