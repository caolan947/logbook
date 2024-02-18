import boto3
import json
import os
from botocore.exceptions import ClientError

# TODO unit test, integration test

client_id = os.environ['account_user_pool_client']

client = boto3.client('cognito-idp')
print(f"Created boto3 client for Cognito")

def lambda_handler(event, context):
    unpacked_event = UnpackSqsMessage(event)
    print(f"Formed message_body {unpacked_event.message_body} to register user in user pool {client_id}")
    
    res = cognito_sign_up(unpacked_event.message_body['username'], unpacked_event.message_body['password'])

    if res["error"]:
        return Response(message=res["message"], status_code=500, data=repr(res["data"])).to_json()
    
    return Response(message=res["message"], data=res["data"]).to_json()

def cognito_sign_up(username, password):
    try:
        res = client.sign_up(
            ClientId=client_id,
            Username=username,
            Password=password
        )

        msg = f"Successfully signed up new user {username} and got response {res}"
        print(msg)

        return {
            "error": False,
            "message": msg,
            "data": res
        } 
    
    except ClientError as e:
        if e.response['Error']['Code'] == 'UsernameExistsException':
            msg = e.response['Error']['Message']
        else:
            msg ="An unexpected error occurred" 
        
        print(msg)  
        
        return {
            "error": True,
            "message": msg,
            "data": e
        } 

class UnpackSqsMessage():
    def __init__(self, event):
        print(event)
        self.event = json.loads(event["Records"][0]['body'])
        self.message_body = {
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

    def to_json(self):
        self.response = {
            "statusCode": self.status_code,
            "body": self.body_content
        }
        
        print(f"Formed response {self.response}")

        return self.response