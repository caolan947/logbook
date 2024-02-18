import unittest
from unittest.mock import patch, Mock
import boto3
from moto import mock_aws
import os

os.environ['account_queue'] = 'fake_queue.fifo'
os.environ['queue_default_group'] = 'fake_group'

from account_handler import app
from botocore.exceptions import ClientError
from aws_lambda_context import LambdaContext

class TestAccountHandlerApp(unittest.TestCase):

    @mock_aws
    def setUp(self):
        self.fake_username = 'fake_username@email.com'
        self.fake_password = 'fake_password'
        self.fake_event = {
            "body": f"{{\"username\": \"{self.fake_username}\", \"password\": \"{self.fake_password}\", \"action\": \"register\"}}"
        }
        self.loaded_body = {"username": self.fake_username, "password": self.fake_password}

        self.fake_client = boto3.client('sqs', region_name="eu-west-1")
        self.fake_queue = self.fake_client.create_queue(
            QueueName='fake_queue.fifo',
            Attributes={'FifoQueue': 'true', 'ContentBasedDeduplication': 'true'
        })
        self.fake_send_message_response = self.fake_client.send_message(
            QueueUrl=self.fake_queue['QueueUrl'],
            MessageBody=self.fake_event['body'],
            MessageGroupId='fake_group'
        )

        self.fake_context = LambdaContext()

        self.fake_unpacked_event = Mock(
            event=self.loaded_body,
            message_body={
                'action': 'register',
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

        self.fake_sqs_send_message_error_false = {
            "error": False,
            "message": f"Successfully sent message to SQS and got response {self.fake_send_message_response}",
            "data": self.fake_send_message_response
        }

        self.fake_sqs_send_message_error_true = {
            "error": True,
            "message": f"An unexpected error occurred when sending message to SQS queue and raised exception {repr(self.fake_exception)}",
            "data": self.fake_exception
        } 

    @patch('account_handler.app.Response')
    @patch.object(app, 'sqs_send_message')
    @patch('account_handler.app.UnpackEvent')
    def test_lambda_handler(self, mock_unpacked_event, mock_res, mock_Response):
        mock_unpacked_event.return_value = self.fake_unpacked_event
        mock_res.return_value = self.fake_sqs_send_message_error_false
        mock_Response.return_value.to_json.return_value = {
            'statusCode': 200,
            'body': self.fake_sqs_send_message_error_false
        } 

        expected_result = {
            'statusCode': 200,
            'body': self.fake_sqs_send_message_error_false
        }
        actual_result = app.lambda_handler(self.fake_event, self.fake_context)
        
        with self.subTest():
            self.assertEqual(expected_result, actual_result)

        mock_res.return_value = self.fake_sqs_send_message_error_true
        mock_Response.return_value.to_json.return_value = {
            'statusCode': 500,
            'body': self.fake_sqs_send_message_error_true
        }

        expected_result = {
            'statusCode': 500,
            'body': self.fake_sqs_send_message_error_true
        }
        actual_result = app.lambda_handler(self.fake_event, self.fake_context)
        
        with self.subTest():
            self.assertEqual(expected_result, actual_result)

    @patch('account_handler.app.client')
    def test_sqs_send_message(self, mock_client):
        mock_client.send_message.return_value = self.fake_send_message_response

        expected_result = self.fake_sqs_send_message_error_false
        actual_result = app.sqs_send_message(self.loaded_body)

        with self.subTest():
            self.assertEqual(expected_result, actual_result)

        mock_client.send_message.side_effect = self.fake_exception

        expected_result = self.fake_sqs_send_message_error_true
        actual_result = app.sqs_send_message(self.loaded_body)

        with self.subTest():
            self.assertEqual(expected_result, actual_result)