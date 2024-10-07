import boto3, os
from moto import mock_aws
from unittest.mock import Mock

from logbook.tests.data import TestData

class AccountHandlerTestData(TestData):

    @mock_aws
    def __init__(self):
        super().__init__()

        self.fake_event = {
            "body": f"{{\"username\": \"{self.fake_username}\", \"password\": \"{self.fake_password}\", \"action\": \"register\"}}"
        }

        self.fake_client = boto3.client("sqs", region_name=os.environ["region"])

        fake_queue = self.fake_client.create_queue(
            QueueName="fake_queue.fifo",
            Attributes={"FifoQueue": "true", "ContentBasedDeduplication": "true"}
        )

        self.fake_send_message_response = self.fake_client.send_message(
            QueueUrl=fake_queue["QueueUrl"],
            MessageBody=self.fake_event["body"],
            MessageGroupId="fake_group"
        )
        
        self.fake_unpacked_event = Mock(
            event=self.user_pw_body,
            message_body={
                "action": "register",
                "username": self.fake_username,
                "password": self.fake_password
            })
        
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

