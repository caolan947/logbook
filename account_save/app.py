import boto3
import json

def lambda_handler(event, context):
    client = boto3.client('cognito-idp')
    print(f"Created boto3 client for Cognito")

    body = json.loads(event['Records'][0]['body'])
    print(f"Unpacked SQS message body for action {body['action']} for username {body['username']} with password {body['password']}")

    try:
        res = client.sign_up(
            ClientId='oktpn5c2mvmcv97mgg08rgcci',
            Username=body['username'],
            Password=body['password']
        )

        msg = f"Successfully signed up new user and got response {res}"
        print(msg)
    
    except Exception as e:
        msg = f"An unexpected error occurred when signing up new user and raised exception {repr(e)}"
        print(msg)

        return {
            "error": True,
            "message": msg,
            "data": e
        }

    return {
        "error": False,
        "message": msg,
        "data": res
    }