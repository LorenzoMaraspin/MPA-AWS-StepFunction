from pybit.unified_trading import HTTP
from aws_lambda_powertools import Logger

logger = Logger()

class BybitApi:
    def __init__(self, config):
        self._config = config
        self._env = True if self._config['env'].lower() == 'dev' else False
        self._session = HTTP(testnet=self._env,api_key=self._config['secret']['api_key'],api_secret=self._config['secret']['api_secret'])

    def switch_margin_mode(self):
        logger.info(f"Trying to switch margin mode: {self._config['position_symbol']}")
        try:
            response = self._session.switch_margin_mode(
                category=self._config['category'],
                symbol=self._config['position_symbol'],
                tradeMode=self._config['trade_mode'],
                buyLeverage=self._config['buy_leverage'],
                sellLeverage=self._config['sell_leverage'],
            )
            if response['retMsg'] == 'OK':
                logger.append_keys(
                    category=self._config['category'],
                    symbol=self._config['position_symbol'],
                    tradeMode=self._config['trade_mode'],
                    buyLeverage=self._config['buy_leverage'],
                    sellLeverage=self._config['sell_leverage']
                )
                logger.info(f"Switched margin mode for position: {self._config['position_symbol']}")
                return True
        except Exception as e:
            logger.exception(f"Unable to switch margin mode position: {self._config['position_symbol']}, {e}")
            if 110026 == e.status_code:
                logger.exception("Cannot switch from Cross to Isolated Margin")
                return False
            else:
                raise e

    def set_leverage(self):
        logger.info(f"Trying to set leverage: {self._config['position_symbol']}")
        try:
            response = self._session.set_leverage(
                category=self._config['category'],
                symbol=self._config['position_symbol'],
                buyLeverage=self._config['buy_leverage'],
                sellLeverage=self._config['sell_leverage']
            )
            if response['retMsg'] == 'OK':
                logger.append_keys(
                    category=self._config['category'],
                    symbol=self._config['position_symbol'],
                    buyLeverage=self._config['buy_leverage'],
                    sellLeverage=self._config['sell_leverage']
                )
                logger.info(f"Setted leverage for position: {self._config['position_symbol']}")
                return True
        except Exception as e:
            logger.exception(f"Unable to set leverage position: {self._config['position_symbol']}, {e}")
            if 110043 == e.status_code:
                logger.exception(e.message)
                return False
            else:
                raise e
    def switch_position_mode(self):
        logger.info(f"Trying to change position mode: {self._config['position_symbol']}")
        try:
            response = self._session.switch_position_mode(
                category=self._config['category'],
                symbol=self._config['position_symbol'],
                mode=self._config['position_mode']
            )
            if response['retMsg'] == 'OK':
                logger.append_keys(
                    category=self._config['category'],
                    symbol=self._config['position_symbol'],
                    mode=self._config['position_mode'],
                    coin=self._config['position_coin']
                )
                logger.info(f"Change position modefor position: {self._config['position_symbol']}")
                return True
        except Exception as e:
            logger.exception(f"Unable to change position mode: {self._config['position_symbol']}, {e}")
            if 110025 == e.status_code:
                logger.exception(e.message)
                return False
            else:
                raise e