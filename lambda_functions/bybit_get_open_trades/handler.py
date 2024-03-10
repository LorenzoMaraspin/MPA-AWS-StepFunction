import json
import os

from bybit_operativity import BybitApi
import boto3
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger

logger = Logger()

def get_config(event):
    logger.info(f"---------- GET and FORMAT EVENT MESSAGE ---------- ")
    config = {key: list(value.values())[0] for key, value in event['result']['Item'].items()}
    config['env'] = os.environ['ENVIRONMENT']
    config['secret_name'] = event['secret_name']
    config['price'] = event['price']
    config['side'] = event['side']

    logger.info(f"Config: {config}", config=config)
    return config

def get_secret(config):
    logger.info(f"---------- GET Secrets Credential ---------- ")
    secret_name = config['secret_name']
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

def lambda_handler(event, context):
    config = get_config(event)
    secret = get_secret(event)
    config['secret'] = secret
    bybit_api = BybitApi(config)

    try:
        position_open = bybit_api.get_position_info()
        if position_open['side'] != "None" and position_open['size'] != "0.000" and position_open['positionValue'] != "0":
            side = 'Sell' if position_open['side'] == 'Buy' else 'Buy'
            logger.info(f"Found open position in: {config['symbol']}")
            position_closed = bybit_api.close_position(side)
        return 0
    except Exception as e:
        logger.exception(f"Unable to get open position due to: {e}")
        raise e