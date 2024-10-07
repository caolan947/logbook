import unittest
from unittest.mock import patch
from .data import AccountHandlerTestData
import os
os.environ["account_queue"] = "fake_queue.fifo"
os.environ["queue_default_group"] = "fake_group"
from account_handler import app

class TestAccountHandlerApp(unittest.TestCase):
    def setUp(self):
        self.test_data = AccountHandlerTestData()

    @patch("account_handler.app.Response")
    @patch.object(app, "sqs_send_message")
    @patch("account_handler.app.EventFactory")
    def test_lambda_handler(self, mock_event, mock_res, mock_Response):
        mock_event.return_value.get_event_parser.return_value = self.test_data.fake_unpacked_event
        mock_res.return_value = self.test_data.fake_sqs_send_message_error_false
        mock_Response.return_value.to_response.return_value = {
            "statusCode": 200,
            "body": repr(self.test_data.fake_sqs_send_message_error_false)
        }

        expected_result = {
            "statusCode": 200,
            "body": repr(self.test_data.fake_sqs_send_message_error_false)
        }
        actual_result = app.lambda_handler(self.test_data.fake_event, self.test_data.fake_context)
        
        with self.subTest():
            self.assertEqual(expected_result, actual_result)

        mock_res.return_value = self.test_data.fake_sqs_send_message_error_true
        mock_Response.return_value.to_response.return_value = {
            "statusCode": 500,
            "body": repr(self.test_data.fake_sqs_send_message_error_false)
        }

        expected_result = {
            "statusCode": 500,
            "body": repr(self.test_data.fake_sqs_send_message_error_false)
        }
        actual_result = app.lambda_handler(self.test_data.fake_event, self.test_data.fake_context)
        
        with self.subTest():
            self.assertEqual(expected_result, actual_result)

    @patch("account_handler.app.client")
    def test_sqs_send_message(self, mock_client):
        mock_client.send_message.return_value = self.test_data.fake_send_message_response

        expected_result = self.test_data.fake_sqs_send_message_error_false
        actual_result = app.sqs_send_message(self.test_data.user_pw_body)

        with self.subTest():
            self.assertEqual(expected_result, actual_result)

        mock_client.send_message.side_effect = self.test_data.fake_exception

        expected_result = self.test_data.fake_sqs_send_message_error_true
        actual_result = app.sqs_send_message(self.test_data.user_pw_body)

        with self.subTest():
            self.assertEqual(expected_result, actual_result)