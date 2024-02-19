import boto3
import json
import os
from botocore.exceptions import ClientError
import logging, logging.config

logging.basicConfig(format='%(levelname)s %(message)s')
logging.config.dictConfig({'version': 1, 'disable_existing_loggers': True})
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers[0].setFormatter(logging.Formatter(fmt='%(filename)s:%(lineno)s - %(funcName)20s() | [%(levelname)s] %(message)s'))

queue_url = os.environ["account_queue"]
msg_group = os.environ["queue_default_group"]
client = boto3.client("sqs", region_name=os.environ["region"])

def lambda_handler(event, context):
    unpacked_event = UnpackEvent(event)
    logger.info(f"Formed message_body {unpacked_event.message_body} to send to queue {queue_url} in group {msg_group}")
    
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
        logger.info(msg)

        return {
            "error": False,
            "message": msg,
            "data": res
        } 
    
    except ClientError as e:
        msg = f"An unexpected error occurred when sending message to SQS queue and raised exception {repr(e)}"
        logger.error(msg)

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
        
        logger.info(f"Unpacked event {event}")

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
            "body": repr(self.body_content)
        }
        
        logger.info(f"Formed response {self.response}")

        return self.response