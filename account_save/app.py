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

client_id = os.environ['account_user_pool_client']
client = boto3.client('cognito-idp', region_name=os.environ["region"])

def lambda_handler(event, context):
    unpacked_message = UnpackSqsMessage(event)
    logger.info(f"Formed message_body {unpacked_message.message_body} to register user in Cognito user pool {client_id}")
    
    res = cognito_sign_up(client_id, unpacked_message.message_body['username'], unpacked_message.message_body['password'])

    if res["error"]:
        return Response(message=res["message"], status_code=500, data=repr(res["data"])).to_json()
    
    return Response(message=res["message"], data=res["data"]).to_json()

def cognito_sign_up(user_pool_client_id, username, password):
    try:
        res = client.sign_up(
            ClientId=user_pool_client_id,
            Username=username,
            Password=password
        )

        msg = f"Successfully signed up new user {username} in Cognito user pool {user_pool_client_id} and got response {res}"
        logger.info(msg)

        return {
            "error": False,
            "message": msg,
            "data": res
        } 
    
    except ClientError as e:
        if e.response['Error']['Code'] == 'UsernameExistsException':
            msg = e.response['Error']['Message']
        else:
            msg = f"An unexpected error occurred when creating user {username} in Cognito user pool {user_pool_client_id} and raised exception {repr(e)}" 
        
        logger.error(msg)  
        
        return {
            "error": True,
            "message": msg,
            "data": e
        } 

class UnpackSqsMessage():
    def __init__(self, event):
        logger.info(event)
        self.event = json.loads(event["Records"][0]['body'])
        self.message_body = {
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

    def to_json(self):
        self.response = {
            "statusCode": self.status_code,
            "body": self.body_content
        }
        
        logger.info(f"Formed response {self.response}")

        return self.response