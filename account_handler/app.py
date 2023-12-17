import boto3
import json

queue_url = 'https://sqs.eu-west-1.amazonaws.com/376949755107/logbook-account-queue-sqs.fifo'
msg_group = 'default-group'

def lambda_handler(event, context):
    client = boto3.client('sqs')
    print(f"Created boto3 client for SQS")

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
            "error": True,
            "message": msg,
            "data": e
        }

    return {
        "error": False,
        "message": msg,
        "data": res
    }