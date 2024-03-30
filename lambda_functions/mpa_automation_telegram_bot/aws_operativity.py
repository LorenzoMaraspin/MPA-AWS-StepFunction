import datetime
import json, uuid
import boto3
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger

logger = Logger()

session = boto3.session.Session()

def create_secret(secret, secret_name):
    client = boto3.client(service_name='secretsmanager')
    secret_string = json.dumps(secret)
    load_date = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    try:
        logger.info("Trying to create a new Secret in AWS")
        response = client.create_secret(
            Name=str(uuid.uuid4()),
            Description='Api key and secret used for trade operativity in Bybit',
            SecretString=secret_string
        )
        if 'ARN' in response and 'Name' in response:
            logger.info("AWS Secret created correctly!")
            return True
    except Exception as e:
        logger.exception("Unable to create a new secret in AWS")
        raise e

def create_dynamodb_item(item):
    client = boto3.resource('dynamodb')
    table = client.Table('UserAccountList')
    logger.info("Trying to create a new user item in DynamoDb table")
    try:
        # Define the item to add
        item = {
            'userId': str(item.id),
            'firstName': item.first_name,
            'lastName': item.last_name,
            'userName': item.username,
            'isBot': item.is_bot,
            'tradeFlag': True
        }
        # Put the item into the table
        response = table.put_item(Item=item)

        if 'Attributes' in response and 'ConsumedCapacity' in response:
            logger.info("Created new record in DynamoDb table")
    except Exception as e:
        logger.exception("Unable to create a new secret in AWS")
        raise e

def update_item_dynamodb(item):
    client = boto3.resource('dynamodb')
    table = client.Table('UserAccountList')
    logger.info("Trying to update user item in DynamoDb table to enable/disable automatic trade")
    try:
        # Define the primary key of the item to update
        key = {'userId': str(item.id)}
        current_item_value = get_item_dynamodb(item.id)
        tradeFlag = False if current_item_value else True
        # Define the update expression and attribute values
        update_expression = 'SET tradeFlag = :val1'
        expression_attribute_values = {
            ':val1': str(tradeFlag)
        }

        # Update the item
        response = table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
    except Exception as e:
        logger.exception("Unable to create a new secret in AWS")
        raise e

def get_item_dynamodb(item):
    client = boto3.resource('dynamodb')
    table = client.Table('UserAccountList')
    logger.info("Trying to get item in DynamoDb table to enable/disable automatic trade")
    try:
        # Define the primary key of the item to update
        key = {'userId': str(item)}

        # Get the item
        response = table.get_item(Key=key)
        if 'Item' in response:
            # Print the item
            item = response['Item']
            logger.info(f"Get item request: {item}")
            return item['tradeFlag']
    except Exception as e:
        logger.exception("Unable to create a new secret in AWS")
        raise e