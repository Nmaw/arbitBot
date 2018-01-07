#!/usr/bin/env python3

# import parallel
# import utility
import sys
import asyncio
import logging
import time
from configparser import ConfigParser, NoSectionError
from modules.datebase import *
from modules.bitfinex_v2 import RESTClient


def main():
    # TODO Read config file
    # TODO Logging all activity
    global collect_symbols

    # Load Config File
    config = ConfigParser()
    configfile = 'main.cfg'
    try:
        config.read(configfile)
        logsfile = config['logs']['logsfile']
    except NoSectionError:
        print('No Config File Found! Exit. #Running in TESTmode!')
        sys.exit()

    # Create Logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # Create file handler and set level to debug
    fh = logging.FileHandler(logsfile, mode='a', encoding=None, delay=False)
    fh.setLevel(logging.DEBUG)
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # Add formatter to handlers
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # Add handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    logger.info('*********************************************************************************')
    logger.info('ABot starting | LogsFile: {} | ConfigFile: {} '.format(logsfile, configfile))

    keys = {}
    database = SQLite()

    for db in config['Exchanges']:
        if config['Exchanges'][db] == 'true':
            logger.info('Reading config file...')
            database.create_db(db, logger)

            keys[db] = ({
                'key': config[db]['key'],
                'sec': config[db]['sec'],
                'buy': config[db]['buy'],
                'sel': config[db]['sel']})

    for item in keys.items():
        logger.info('Exchange config: {}'.format(item))

    margin = config['margin']['percentage']

    logger.info('Margin in percentage: {} %'.format(margin))
    logger.info('Config file {} was loaded'.format(configfile))

    i = 0
    conn = None

    while i < 5:
        loop = asyncio.get_event_loop()
        exch = RESTClient(loop)

        for dbname in keys.keys():
            print(dbname)

            if conn is None:
                conn, cursor = database.connect(dbname, logger)

            async def collect_symbols(loop):
                symbols = await exch.symbols()
                symbols_details = await exch.symbols_details()

                for tablename in symbols:
                    database.create_table(conn, cursor, tablename, logger)
                    # TODO Создаем таблицу symbols_details и задаем ее структуру, после этого отправялемся все создавать иначе ни как

                # print(symbols)
                # print(symbols_details)

        async def collect_fundingbook(loop):
            bitfinex = RESTClient(loop)
            fundingbook = await bitfinex.funding_book('usd')

            # print(fundingbook)

        async def collect_lends(loop):
            bitfinex = RESTClient(loop)
            lends = await bitfinex.lends('usd')

            # print(lends)

        async def collect_orders(loop):
            bitfinex = RESTClient(loop)
            order = await bitfinex.order_book('btcusd')

            # print(order)

        async def collect_trades(loop):
            bitfinex = RESTClient(loop)
            trades = await bitfinex.trades('btcusd')

            # print(trades)

        async def collect_tickers(loop):
            bitfinex = RESTClient(loop)
            ticker = await bitfinex.ticker('btcusd')

            # print(ticker)

        async def collect_stats(loop):
            bitfinex = RESTClient(loop)
            stats = await bitfinex.stats('btcusd')

            # print(stats)

        # loop.run_until_complete(collect_tickers(loop))
        # loop.run_until_complete(collect_trades(loop))
        # loop.run_until_complete(collect_orders(loop))
        loop.run_until_complete(collect_symbols(loop))
        # loop.run_until_complete(collect_stats(loop))
        # loop.run_until_complete(collect_fundingbook(loop))
        # loop.run_until_complete(collect_lends(loop))
        i += 1

    def quit_app():
        #logger.info('KeyboardInterrupt, quitting!')
        sys.exit()


if __name__ == '__main__':
    main()
