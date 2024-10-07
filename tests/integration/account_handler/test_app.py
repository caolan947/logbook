from unittest import TestCase
import os, requests, boto3
from botocore.exceptions import ClientError
from ...data import TestData

class TestAccountHandler(TestCase):

    def setUp(self):
        self.test_data = TestData()

    def test_account_handler(self):
        headers = headers = {'Content-type': 'application/json', 'Accept':'application/json'}
        
        actual_result = requests.post(
            os.environ['API_ENDPOINT'],
            json=self.test_data.user_pw_body,
            headers=headers
        )

        with self.subTest():
            self.assertTrue(actual_result.ok)
        
    def tearDown(self):
        client = boto3.client(
            "cognito-idp",
            region_name=os.environ["region"],
            aws_access_key_id=os.environ['PIPELINE_TESTER_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['PIPELINE_TESTER_SECRET_ACCESS_KEY']
        )
        
        try:
            client.admin_delete_user(
                UserPoolId=f"{os.environ['region']}_jGwoeJ8Q0",
                Username=self.test_data.fake_username
            )

        except ClientError as e:
            pass