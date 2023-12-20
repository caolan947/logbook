import boto3
import json
import os

# TODO unit test, integration test

queue_url = os.environ['account_queue']
msg_group = os.environ['queue_default_group']

client = boto3.client('sqs')
print(f"Created boto3 client for SQS")

def lambda_handler(event, context):
    event = json.loads(event['body'])
    message_body = {
        'action': 'register_account',
        'username': event['username'],
        'password': event['password']
    }
    print(f"Formed message_body {message_body} to send to queue {queue_url} in group {msg_group}")

    try:
        res = client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message_body),
            MessageGroupId=msg_group
        )

        msg = f"Successfully sent message to SQS and got response {res}"
        print(msg)
    
    except Exception as e:
        msg = f"An unexpected error occurred when sending message to SQS queue and raised exception {repr(e)}"
        print(msg)

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": True,
                "message": msg,
                "data": repr(e)
            })
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "error": False,
            "message": msg,
            "data": res
        })
    }