import boto3, os
from botocore.exceptions import ClientError
import logging, logging.config
from lambdarepy import EventFactory, Response

logging.basicConfig(format='%(levelname)s %(message)s')
logging.config.dictConfig({'version': 1, 'disable_existing_loggers': True})
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers[0].setFormatter(logging.Formatter(fmt='%(filename)s:%(lineno)s - %(funcName)20s() | [%(levelname)s] %(message)s'))

client_id = os.environ['account_user_pool_client']
client = boto3.client('cognito-idp', region_name=os.environ["region"])
print(f"Created Cognito client in {os.environ['region']}")

def lambda_handler(event, context):
    unpacked_message = EventFactory(event).get_event_parser()
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