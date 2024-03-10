import json
import os
import boto3
from aws_lambda_powertools import Logger

logger = Logger()


def lambda_handler(event, context):
    logger.info("---------- GET Number of Account Active ----------")
    parameter_name = os.environ['SSM_PARAMETER_ACCOUNT_ACTIVE']
    logger.info(f"Parameter to read: {parameter_name}")
    parameter_value = get_ssm_parameter_and_convert(parameter_name)

    return parameter_value


def get_ssm_parameter_and_convert(name):
    # Create a client
    ssm = boto3.client('ssm')
    logger.info("---------- GET Parameter value and Convert to List ----------")
    try:
        # Get the parameter
        response = ssm.get_parameter(Name=name, WithDecryption=True)
        if response['Parameter']['Value']:
            param_value = response['Parameter']['Value']
            list_value = param_value.split(',')
            return list_value
    except Exception as e:
        logger.exception(f"Unable to get parameter {e}")
        raise e