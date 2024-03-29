from unittest import TestCase
import os
import requests
import boto3
from botocore.exceptions import ClientError

class TestAccountHandler(TestCase):

    def setUp(self):
        self.api_endpoint = os.environ['API_ENDPOINT']
        self.username = "test1@email.com"

        self.event = {"username": self.username, "password": "password1"}

    def test_account_handler(self):
        headers = headers = {'Content-type': 'application/json', 'Accept':'application/json'}
        
        actual_result = requests.post(self.api_endpoint, json=self.event, headers=headers)

        with self.subTest():
            self.assertTrue(actual_result.ok)
        
    def tearDown(self):
        client = boto3.client("cognito-idp",region_name="eu-west-1",aws_access_key_id=os.environ['PIPELINE_TESTER_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['PIPELINE_TESTER_SECRET_ACCESS_KEY'])
        
        try:
            client.admin_delete_user(UserPoolId="eu-west-1_jGwoeJ8Q0", Username=self.username)
        except ClientError as e:
            pass