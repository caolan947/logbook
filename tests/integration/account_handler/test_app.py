from unittest import TestCase
import os
import requests

import boto3

class TestApiGateway(TestCase):

    def setUp(self):
        self.api_endpoint = os.environ['api-endpoint']
        self.username = "test1@email.com"

        self.event = {"username": self.username, "password": "password1"}

    def tearDown(self):
        client = boto3.client("cognito-idp",  region_name="eu-west-1")
        client.admin_delete_user(UserPoolId=os.environ["queue_default_group"], Username=self.username)

    def test_api_gateway(self):
        headers = headers = {'Content-type': 'application/json', 'Accept':'application/json'}
        
        actual_result = requests.post(self.api_endpoint, json=self.event, headers=headers)

        with self.subTest():
            self.assertTrue(actual_result.ok)