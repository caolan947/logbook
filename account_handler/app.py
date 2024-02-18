import boto3
import json
import os
from botocore.exceptions import ClientError

queue_url = os.environ["account_queue"]
msg_group = os.environ["queue_default_group"]

client = boto3.client("sqs", region_name="eu-west-1")
print(f"Created boto3 client for SQS")

def lambda_handler(event, context):
    unpacked_event = UnpackEvent(event)
    print(f"Formed message_body {unpacked_event.message_body} to send to queue {queue_url} in group {msg_group}")
    
    res = sqs_send_message(unpacked_event.message_body)

    if res["error"]:
        return Response(message=res["message"], status_code=500, data=repr(res["data"])).to_response()

    return Response(message=res["message"], data=res["data"]).to_response()

def sqs_send_message(message_body):
    try:
        res = client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message_body),
            MessageGroupId=msg_group
        )

        msg = f"Successfully sent message to SQS and got response {res}"
        print(msg)

        return {
            "error": False,
            "message": msg,
            "data": res
        } 
    
    except ClientError as e:
        msg = f"An unexpected error occurred when sending message to SQS queue and raised exception {repr(e)}"
        print(msg)

        return {
            "error": True,
            "message": msg,
            "data": e
        } 

class UnpackEvent():
    def __init__(self, event):
        self.event = json.loads(event["body"])
        self.message_body = {
            "action": "register",
            "username": self.event["username"],
            "password": self.event["password"]
        }
        
        print(f"Unpacked event {event}")

class Response():
    def __init__(self, message, status_code=200, error=False, data=None):
        self.message = message
        self.status_code = status_code
        self.error = error
        self.data=data
        
        if self.status_code != 200:
            self.error = True
            self.data = self.data

        self.body_content = {
            "error": self.error,
            "message": message,
            "data": self.data
        }

    def to_response(self):
        self.response = {
            "statusCode": self.status_code,
            "body": self.body_content
        }
        
        print(f"Formed response {self.response}")

        return json.loads(self.response)