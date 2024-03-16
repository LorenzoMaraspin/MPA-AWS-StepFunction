from pybit.unified_trading import HTTP
from aws_lambda_powertools import Logger

logger = Logger()

class BybitApi:
    def __init__(self, config):
        self._config = config
        self._env = True if self._config['env'].lower() == 'dev' else False
        self._session = HTTP(testnet=self._env,api_key=self._config['secret']['api_key'],api_secret=self._config['secret']['api_secret'])

    def set_tp_sl(self, order, mode):
        logger.info(f"Trying to set TP/SL for order: {self._config['position_symbol']}")
        try:
            response = self._session.set_trading_stop(
                category=self._config['category'],
                symbol=self._config['position_symbol'],
                takeProfit=order['tp'],
                stopLoss=order['sl'],
                tpTriggerBy="MarkPrice",
                slTriggerB="MarkPrice",
                tpslMode=mode,
                tpSize=order['size'],
                slSize=order['size'],
                positionIdx=0
            )
            if response['retMsg'] == 'OK':
                logger.append_keys(
                    takeProfit=order['tp'],
                    stopLoss=order['sl'],
                    tpslMode=mode,
                    tpSize=order['size'],
                    slSize=order['size'],
                )
                logger.info(f"Setted up TP/SL for position: {self._config['position_symbol']}")
        except Exception as e:
            logger.info(f"Unable to set TP/SL details for position: {self._config['position_symbol']}, {e}")
            raise e

    def get_wallet_balance(self):
        logger.info(f"Trying to get wallet balance details")
        try:
            response = self._session.get_wallet_balance(
                accountType=self._config['account_type'],
                coin="USDT",
            )
            if response['retMsg'] == 'OK':
                logger.info(f"Wallet balance details received correctly: {response['retMsg']}")
                return response['result']['list'][0]

        except Exception as e:
            logger.info(f"Unable to get wallet balance details : {e}")
            raise e

    def open_position(self, qty):
        side = 'Buy' if self._config['side'] == 'Long' else 'Sell'
        logger.info(f"Trying to open trade: {self._config['side']}")
        try:
            response = self._session.place_order(
                category=self._config['category'],
                symbol=self._config['position_symbol'],
                side=side,
                orderType=self._config['order_type'],
                qty=str(qty),
                reduceOnly=False
            )
            logger.append_keys(
                order_id=response['result']['orderId'],
                side=side,
                symbol=self._config['position_symbol'],
                qty=qty
            )
            logger.info(f"Opened trade: {self._config['side']}")
            return {"orderId": response['result']['orderId'], "timeStamp": response['time']}
        except Exception as e:
            logger.error(f"Unable to open trade due: {e}")
            raise e