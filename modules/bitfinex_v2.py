import asyncio
import logging
import async_timeout
import base64
import hashlib
import time
import hmac
import json
import aiohttp

from typing import Optional, List, Tuple

# @author Julioocz/aiobitfinex with modification @Nmaw

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bitfinex.rest')


class NoAPIKeys(Exception):
    pass


class APIPath:
    """Path definitions for the Bitfinex REST API"""

    API_ROOT = 'https://api.bitfinex.com/v1/{}'

    # -- Public endpoints. http://docs.bitfinex.com/v1/reference

    SYMBOLS = API_ROOT.format('symbols')
    SYMBOLS_DETAILS = API_ROOT.format('symbols_details')

    # - Uses symbol (btcusd, etc)
    TICKER = API_ROOT.format('pubticker/{}')
    STATS = API_ROOT.format('stats/{}')
    TRADES = API_ROOT.format('trades/{}')

    # - Uses currency ('USD, etc)
    FUNDING_BOOK = API_ROOT.format('lendbook/{}')
    ORDER_BOOK = API_ROOT.format('book/{}')
    LENDS = API_ROOT.format('lends/{}')

    # -- Authenticated endpoints. http://docs.bitfinex.com/v1/reference#rest-auth-account-info
    ACCOUNT_INFO = API_ROOT.format('account_infos')
    SUMMARY = API_ROOT.format('summary')
    DEPOSIT = API_ROOT.format('deposit/new')
    KEY_PERMISSIONS = API_ROOT.format('key_info')
    MARGIN_INFO = API_ROOT.format('margin_infos')
    BALANCES = API_ROOT.format('balances')
    TRANSFER = API_ROOT.format('transfer')
    WITHDRAWAL = API_ROOT.format('withdraw')

    # - Orders. http://docs.bitfinex.com/v1/reference#rest-auth-orders
    ACTIVE_ORDERS = API_ROOT.format('orders')
    ORDER_ROOT = API_ROOT.format('order/{}')
    NEW_ORDER = ORDER_ROOT.format('new')
    NEW_ORDER_MULTI = ORDER_ROOT.format('new/multi')
    CANCEL_ORDER = ORDER_ROOT.format('cancel')
    CANCEL_ORDER_MULTI = ORDER_ROOT.format('cancel/multi')
    CANCEL_ORDER_ALL = ORDER_ROOT.format('cancel/all')
    REPLACE_ORDER = ORDER_ROOT.format('replace')
    STATUS_ORDER = ORDER_ROOT.format('status')

    # - Positions. http://docs.bitfinex.com/v1/reference#rest-auth-positions
    ACTIVE_POSITIONS = API_ROOT.format('positions')
    CLAIM_POSITION = API_ROOT.format('position/claim')

    # - Historical data. http://docs.bitfinex.com/v1/reference#rest-auth-historical-data
    HISTORY = API_ROOT.format('history')
    MOVEMENTS = API_ROOT.format('history/movements')
    PAST_TRADES = API_ROOT.format('mytrades')

    # - Marging Funding. http://docs.bitfinex.com/v1/reference#rest-auth-margin-funding
    OFFERS = API_ROOT.format('offers')
    OFFER_ROOT = API_ROOT.format('offer/{}')
    NEW_OFFER = OFFER_ROOT.format('new')
    CANCEL_OFFER = OFFER_ROOT.format('cancel')
    STATUS_OFFER = OFFER_ROOT.format('status')

    ACTIVE_CREDITS = API_ROOT.format('credits')
    TAKEN_FUNDS = API_ROOT.format('taken_funds')
    UNUSED_TAKEN_FUNDS = API_ROOT.format('unused_taken_funds')
    TOTAL_TAKEN_FUNDS = API_ROOT.format('total_taken_funds')
    CLOSE_FUNDING = API_ROOT.format('funding/close')


class RESTClient:
    """
    Async client for the bitfinex HTTP REST API.
    """

    def __init__(self,
                 api_key: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 loop: Optional[asyncio.BaseEventLoop] = None,
                 session: aiohttp.ClientSession = None):

        self._loop = loop or asyncio.get_event_loop()
        self._session = session or aiohttp.ClientSession(loop=self._loop)

        # Setting a property `keys` if the keys were provided. They are needed for the private enpoints
        if api_key and api_secret:
            self._api_key = api_key
            self._api_secret = bytes(api_secret, 'utf-8')
            self.keys = True
        else:
            self.keys = False
            logger.warning('The API keys was not provided. The authenticated API methdos wont be available')

    def __del__(self):
        if not self._session.closed:
            self._session.close()

    def _prepare_post(self, url: str, payload: dict) -> Tuple[any, dict]:
        """
        Adds the nonce to the payload. Encodes it with base64. Makes a signature with it
        and the api key secret. Returning the auth headers that should be used in the request
        :payload: the payload that's going to be send to the private endpoint
        :url: api url to be used to get the api enpoint required on the payload dict
        :return: the headers auth headers that should be send with the request
        """
        # Adding the url endpoint to the request. Striping https://api.bitfinex.com
        payload['request'] = '/{}'.format('/'.join(url.split('/')[3:]))

        # Adding nonce to the payload
        payload['nonce'] = str(time.time())

        payload_json = json.dumps(payload)
        payload_b64 = base64.b64encode(bytes(payload_json, 'utf-8'))

        signature = hmac.new(key=self._api_secret, msg=payload_b64, digestmod=hashlib.sha384)
        signature = signature.hexdigest()

        headers = {
            'X-BFX-APIKEY': self._api_key,
            'X-BFX-PAYLOAD': str(payload_b64, 'utf-8'),
            'X-BFX-SIGNATURE': signature,
        }
        return payload_b64, headers

    async def _post(self, url, payload=None) -> any:
        """
        Performs a POST request, checking if the user is authenticated to create the auth
        headers. If the user is not authenticated it raises an error.
        The response code is checkied to se if it's beteween 200 -- 300. If it's, it parses the
        JSON response to a python object. If not it raises a HTTP erro
        :param url: the api url
        :param payload: the payload to be send with the request
        :return: The Bitfinex API response
        """
        # Checking keys
        if not self.keys:
            raise NoAPIKeys('The private endpoints require the api keys')

        payload = payload or {}
        payload_encoded, headers = self._prepare_post(url, payload)

        logger.debug('Sending post request to {}'.format(url))
        with async_timeout.timeout(20):
            async with self._session.post(url, data=payload_encoded, headers=headers) as resp:
                if 200 <= resp.status < 300:
                    return await resp.json()
                else:
                    print(resp.text())
                    logger.warning('There was a problem processing {}, with status {}'.format(url, resp.status))

    async def _fetch(self, url: str) -> any:
        """
        Performs a GET request, checking the response code to see if it's between 200 - 300.
        If it's, it parses the JSON to a python object. If not it raises an HTTP error
        :url: the api url
        :return: The Bitfinex API response
        """
        logger.debug('Fetching {}'.format(url))
        with async_timeout.timeout(15):
            async with self._session.get(url) as resp:
                if 200 <= resp.status < 300:
                    return await resp.json()
                else:
                    print(resp.json())
                    logger.warning('There was a problem processing {}, with status {}'.format(url, resp.status))

    async def ticker(self, symbol: str) -> dict:
        """
        Gets the high level overview of the state of the market (ticker) for the given symbol
        API URL: http://docs.bitfinex.com/v1/reference#rest-public-ticker
        :param symbol: the currency pair that you want information. (btcusd, etc). Yo can look
        at the available symbols with the symbol method.
        :return:
        """
        time.sleep(5)
        #TODO Create new method for delay
        return await self._fetch(APIPath.TICKER.format(symbol))

    async def stats(self, symbol: str) -> dict:
        """
        Gets various statistics about the requested pair (symbol)
        API URL: http://docs.bitfinex.com/v1/reference#rest-public-stats
        :param symbol: the currency pair that you want information. (btcusd, etc). Yo can look
        at the available symbols with the symbol method.
        :return: stats about the requested pair
        """
        time.sleep(15)
        #TODO Create new method for delay

        return await self._fetch((APIPath.STATS.format(symbol)))

    async def trades(self, symbol: str) -> List[dict]:
        """
        Gets the most recent trades for the given symbol
        API URL: http://docs.bitfinex.com/v1/reference#rest-public-trades
        :param symbol: the currency pair that you want information. (btcusd, etc). Yo can look
        at the available symbols with the symbol method.
        :return: a list with the most recent trades
        """
        return await self._fetch(APIPath.TRADES.format(symbol))

    async def funding_book(self, currency: str) -> dict:
        """
        Gets the full margin funding book
        API URL: http://docs.bitfinex.com/v1/reference#rest-public-fundingbook
        :param currency: the currency in what you want the information
        :return:
        """
        return await self._fetch((APIPath.FUNDING_BOOK.format(currency)))

    async def order_book(self, currency: str) -> dict:
        """
        Gets the full order book
        API URL: http://docs.bitfinex.com/v1/reference#rest-public-orderbook
        :param currency: the currency in what you want the information
        :return:
        """
        return await self._fetch(APIPath.ORDER_BOOK.format(currency))

    async def lends(self, currency: str) -> List[dict]:
        """
        Gets a list of the most recent funding data for the given currency
        :param currency:
        :return:
        """
        return await self._fetch(APIPath.LENDS.format(currency))

    async def symbols(self) -> List[dict]:
        """Gets a list with the available symbol names in the exchange"""
        return await self._fetch(APIPath.SYMBOLS)

    async def symbols_details(self) -> List[dict]:
        """Gets a detailed list with the available symbols on the exchange"""
        return await self._fetch(APIPath.SYMBOLS_DETAILS)

    # Authenticated methods
    async def account_info(self) -> List[dict]:
        """
        Returns information about the trading fees of the authenticated account
        API URL: http://docs.bitfinex.com/v1/reference#rest-auth-account-info
        :return: A list with the trading fees from the currency pairs
        """
        return await self._post(APIPath.ACCOUNT_INFO)

    async def summary(self) -> dict:
        """
        Returns a 30-day summary of your trading volume and return on marging funding
        API URL: http://docs.bitfinex.com/v1/reference#rest-auth-summary
        :return: a dict with the summary
        """
        return await self._post(APIPath.SUMMARY)

    async def deposit(self, method, wallet_name, renew: Optional[bool] = False) -> str:
        """
        Returns your deposited address to make a new deposit
        API URL: http://docs.bitfinex.com/v1/reference#rest-auth-deposit
        :param method: method of deposit. (bitcoin, litecoin, ethereum, mastercoin,
         ethereumc, zcash, monero)
        :param wallet_name: wallet to deposit int (trading, exchange, deposit). Your
        wallet nerds to already exist
        :param renew: Default is False. If set to True, will return a new unused deposit address
        :return: the address to be used on the deposit
        """
        payload = {
            'method': method,
            'wallet_name': wallet_name,
            'renew': 1 if renew else 0
        }
        resp = await self._post(APIPath.DEPOSIT, payload)
        return resp['address']

    async def key_info(self) -> dict:
        """Returns the permissions of the api key that were used on the constructor"""
        return await self._post(APIPath.KEY_PERMISSIONS)

    async def margin_info(self):
        """
        Returns your trading wallet information for margin trading
        API URL: http://docs.bitfinex.com/v1/reference#rest-auth-margin-information
        """
        return await self._post(APIPath.MARGIN_INFO)

    async def balances(self):
        """
        Returns the balances of your wallets
        API URL: http://docs.bitfinex.com/v1/reference#rest-auth-wallet-balances
        """
        return await self._post(APIPath.BALANCES)

    async def transfer(self, amount: float, currency: str, wallet_from: str, wallet_to: str):
        """
        Allows you to move your available blanaces between wallets
        API URL: http://docs.bitfinex.com/v1/reference#reast-auth-transfer-between-wallets
        :amount: amount to be transfered on the given currency
        :currency: currency of funds to transfer
        :return: a dict with the status (success or error) and a status message
        """
        payload = {
            'amount': amount,
            'currency': currency,
            'walletfrom': wallet_from,
            'walletto': wallet_to
        }
        return (await self._post(APIPath.TRANSFER, payload))[0]

    async def withdraw(self,
                       withdrawal_type: str,
                       wallet_elected: str,
                       amount: float,
                       address: str,
                       account_number: str,
                       bank_name: str,
                       bank_address: str,
                       bank_city: str,
                       bank_country: str,
                       swift: str=None,
                       detail_payment: str=None,
                       expressWire: bool=0,  # noqa
                       payment_id: str=None,
                       account_name: str=None,
                       intermediary_bank_name: str=None,
                       intermediary_bank_address: str=None,
                       intermediary_bank_city: str=None,
                       intermediary_bank_country: str=None,
                       intermediary_bank_account: str=None,
                       intermediary_bank_swift: str=None) -> dict:
        """
        Allow you to request a withdrawal from one of your wallet.
        API URL: http://docs.bitfinex.com/v1/reference#rest-auth-withdrawal
        Check the api docs for more info about the params
        :param withdrawal_type:
        :param wallet_elected:
        :param amount:
        :param address:
        :param account_number:
        :param bank_name:
        :param bank_address:
        :param bank_city:
        :param bank_country:
        :param swift:
        :param detail_payment:
        :param expressWire:
        :param payment_id:
        :param account_name:
        :param intermediary_bank_name:
        :param intermediary_bank_address:
        :param intermediary_bank_city:
        :param intermediary_bank_country:
        :param intermediary_bank_account:
        :param intermediary_bank_swift:
        :return: a dict with the status, message and withdrawal_id
        """

        payload = {key: value for key, value in locals().items() if value}
        return (await self._post(APIPath.WITHDRAWAL, payload))[0]
