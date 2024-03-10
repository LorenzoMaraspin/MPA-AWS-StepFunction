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
    config['position_size'] = os.environ['POSITION_SIZE']
    config['operativity_user_option'] = os.environ['OPERATIVITY_USER_CHOICE']
    config['operativity_options'] = get_parameter_value(os.environ['OPERATIVITY_OPTIONS'])[config['operativity_user_option']]

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

def can_deserialize(s):
    try:
        json.loads(s)
        return True
    except json.JSONDecodeError:
        return False

def get_parameter_value(parameter_name):
    ssm = boto3.client('ssm')
    try:
        response = ssm.get_parameter(Name=parameter_name)
        if can_deserialize(response['Parameter']['Value']):
            deserialized = json.loads(response['Parameter']['Value'])
            return deserialized
        else:
            return response['Parameter']['Value']
    except ClientError as e:
        raise e
def calculate_position_size(config,balance):
    wallet_balance_to_withdraw = float(balance['coin'][0]['availableToWithdraw'])
    leverage = int(config['buy_leverage'])
    risk = float(config['position_size'])

    quantity = (wallet_balance_to_withdraw * risk * leverage) / float(config['price'])

    logger.append_keys(
        balance=wallet_balance_to_withdraw,
        leverage=leverage,
        risk=risk,
        quantity=f"{quantity:.3f}"
    )
    logger.info("Calculated the quantity used to open a position")
    qty = f"{quantity:.2f}"
    return qty

def calculate_tp_sl_trade(config, type_op, value):
    price = config['price']
    side = config['side']
    if type_op == 'tp':
        if side == 'Buy':
            result = f"{float(price) + (float(price) * value /100):.4f}"
        else:
            result = f"{float(price) - (float(price) * value / 100):.4f}"
    else:
        if side == 'Buy':
            result = f"{float(price) - (float(price) * value / 100):.4f}"
        else:
            result = f"{float(price) + (float(price) * value / 100):.4f}"

    logger.info(f"Defined: {type_op} value = {result}")

    return result

def lambda_handler(event, context):
    config = get_config(event)
    secret = get_secret(event)
    config['secret'] = secret
    bybit_api = BybitApi(config)
    try:
        wallet_balance = bybit_api.get_wallet_balance()
        position_size = calculate_position_size(config,wallet_balance)
        bybit_api.open_position(position_size)

    except Exception as e:
        logger.exception(f"Unable to open new trade due: {e}")
        raise e



