from pybit.unified_trading import HTTP
from aws_lambda_powertools import Logger

logger = Logger()

class BybitApi:
    def __init__(self, config):
        self._config = config
        self._env = True if self._config['env'].lower() == 'dev' else False
        self._session = HTTP(testnet=self._env,api_key=self._config['secret']['api_key'],api_secret=self._config['secret']['api_secret'])

    def get_position_info(self):
        logger.info(f"Trying to get open trade")
        try:
            response = self._session.get_positions(
                category=self._config['category'],
                symbol=self._config['position_symbol'],
            )
            logger.append_keys(
                category=self._config['category'],
                symbol=self._config['position_symbol'],
            )
            if response['retMsg'] == 'OK':
                result = response['result']['list'][0]
                return result
        except Exception as e:
            logger.error(f"Unable to get trade due: {e}")
            raise e

    def close_position(self, side):
        logger.info(f"Trying to close trade: {side}")
        try:
            response = self._session.place_order(
                category=self._config['category'],
                symbol=self._config['position_symbol'],
                side=side,
                orderType=self._config['order_type'],
                qty=0,
                positionIdx=0,
                marketUnit=self._config['market_unit'],
                reduceOnly=True
            )
            logger.append_keys(
                order_id=response['result']['orderId'],
                side=side,
                symbol=self._config['position_symbol'],
                qty=0
            )
            logger.info(f"Closed trade: {side}")
            return {"orderId": response['result']['orderId'], "timeStamp": response['time']}
        except Exception as e:
            logger.error(f"Unable to close trade due: {e}")