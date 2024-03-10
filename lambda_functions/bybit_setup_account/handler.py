import json
from bybit_operativity import BybitApi
import boto3
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger

logger = Logger()


def get_config(event):
    logger.info(f"---------- GET and FORMAT EVENT MESSAGE---------- ")
    config = {key: list(value.values())[0] for key, value in event['items'].items()}
    config['env'] = event['environment']
    config['secret_name'] = event['secret_name']

    logger.info(f"Config: {config}", config=config)
    return config


def get_secret(event):
    logger.info(f"---------- GET Secrets Credential ---------- ")
    secret_name = event['secret_name']
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
    secret = get_secret(event)
    config = get_config(event)
    config['secret'] = secret

    bybit = BybitApi(config)

    try:
        response_margin_mode = bybit.switch_margin_mode()
        response_set_leverage = bybit.set_leverage()
        response_position_mode = bybit.switch_position_mode()

        return {"status_code": 200, "result": f"Bybit account properly configured for symbol: {config['symbol']}",
                "secret_name": config['secret_name']}
    except Exception as e:
        raise e
