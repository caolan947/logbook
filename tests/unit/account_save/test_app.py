import unittest
from unittest.mock import patch
from .data import AccountSaveTestData
import os
os.environ["account_user_pool_client"] = "fake_id"
from account_save import app

class TestAccountSaveApp(unittest.TestCase):
    def setUp(self):
        self.test_data = AccountSaveTestData()

    @patch("account_save.app.Response")
    @patch.object(app, "cognito_sign_up")
    @patch("account_save.app.EventFactory")
    def test_lambda_handler(self, mock_unpacked_unpacked_message, mock_res, mock_Response):
        mock_unpacked_unpacked_message.return_value.get_event_parser.return_value = self.test_data.fake_unpacked_message
        mock_res.return_value = self.test_data.fake_cognito_sign_up_error_false
        mock_Response.return_value.to_json.return_value = {
            "statusCode": 200,
            "body": self.test_data.fake_cognito_sign_up_error_false
        } 

        expected_result = {
            "statusCode": 200,
            "body": self.test_data.fake_cognito_sign_up_error_false
        }
        actual_result = app.lambda_handler(self.test_data.fake_event, self.test_data.fake_context)
        
        with self.subTest():
            self.assertEqual(expected_result, actual_result)

        mock_res.return_value = self.test_data.fake_cognito_sign_up_error_true_user_exists
        mock_Response.return_value.to_json.return_value = {
            "statusCode": 500,
            "body": self.test_data.fake_cognito_sign_up_error_true_user_exists
        }

        expected_result = {
            "statusCode": 500,
            "body": self.test_data.fake_cognito_sign_up_error_true_user_exists
        }
        actual_result = app.lambda_handler(self.test_data.fake_event, self.test_data.fake_context)
        
        with self.subTest():
            self.assertEqual(expected_result, actual_result)
    
    @patch("account_save.app.client")
    def test_cognito_sign_up(self, mock_client):
        mock_client.sign_up.return_value = self.test_data.fake_sign_up_response

        expected_result = self.test_data.fake_cognito_sign_up_error_false
        actual_result = app.cognito_sign_up(self.test_data.fake_client_id, self.test_data.user_pw_body["username"], self.test_data.user_pw_body["password"])

        with self.subTest():
            self.assertEqual(expected_result, actual_result)

        mock_client.sign_up.side_effect = self.test_data.fake_exception

        expected_result = self.test_data.fake_cognito_sign_up_error_true_generic
        actual_result = app.cognito_sign_up(self.test_data.fake_client_id, self.test_data.user_pw_body["username"], self.test_data.user_pw_body["password"])

        with self.subTest():
            self.assertEqual(expected_result, actual_result)

        mock_client.sign_up.side_effect = self.test_data.fake_user_exists_exception

        expected_result = self.test_data.fake_cognito_sign_up_error_true_user_exists
        actual_result = app.cognito_sign_up(self.test_data.fake_client_id, self.test_data.user_pw_body["username"], self.test_data.user_pw_body["password"])

        with self.subTest():
            self.assertEqual(expected_result, actual_result)