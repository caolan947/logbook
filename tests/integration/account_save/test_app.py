from unittest import TestCase
import json
import boto3
from botocore.exceptions import ClientError
import time
import os

class TestAccountSave(TestCase):

    def setUp(self):
        self.username = "test1@email.com"

        self.message_body = {"username": self.username, "password": "password1"}
        
        self.sqs_client = boto3.client("sqs", region_name="eu-west-1",aws_access_key_id=os.environ['PIPELINE_TESTER_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['PIPELINE_TESTER_SECRET_ACCESS_KEY'])
        self.cognito_client = boto3.client("cognito-idp", region_name="eu-west-1",aws_access_key_id=os.environ['PIPELINE_TESTER_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['PIPELINE_TESTER_SECRET_ACCESS_KEY'])

    def test_account_save(self):
        r = self.sqs_client.send_message(
            QueueUrl='logbook-account-queue-sqs.fifo',
            MessageBody=json.dumps(self.message_body),
            MessageGroupId='msg_group'
        )

        time.sleep(3)

        actual_result = self.cognito_client.list_users(
            UserPoolId="eu-west-1_jGwoeJ8Q0",
            Filter=f"email='{self.username}'"
        )


        with self.subTest():
            self.assertTrue(len(actual_result['Users']), 1)

    def tearDown(self):
        try:
            self.cognito_client.admin_delete_user(UserPoolId="eu-west-1_jGwoeJ8Q0", Username=self.username)
        except ClientError as e:
            pass