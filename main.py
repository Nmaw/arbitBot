#!/usr/bin/env python3

# import parallel
# import utility
from configparser import ConfigParser, NoSectionError
import logging
import sys
from modules.datebase import *
from modules.bitfinex_v2 import *

# Create Logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def main():
    # TODO Read config file
    # TODO Logging all activity

    # Load Config File
    config = ConfigParser()
    configfile = 'main.cfg'
    try:
        config.read(configfile)
        logsfile = config['logs']['logsfile']
    except NoSectionError:
        print('No Config File Found! Exit. #Running in TESTmode!')
        sys.exit()

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

    logger.info('ABot starting | LogsFile: {} | ConfigFile: {} '.format(logsfile, configfile))

    keys = {}
    database = SQLite()

    for db in config['Exchanges']:
        if config['Exchanges'][db] == 'true':
            # Create DBs
            database.create_db(db, logger)
            logger.info('Database data/{}.sqlite was created'.format(db))

            keys[db] = ({
                'key': config[db]['key'],
                'sec': config[db]['sec'],
                'buy': config[db]['buy'],
                'sel': config[db]['sel']})
            logger.info('Reading config file...')

    for item in keys.items():
        logger.info('Exchange config: {}'.format(item))

    margin = config['margin']['percentage']

    logger.info('Margin in percentage: {} %'.format(margin))
    logger.info('Config file {} was loaded'.format(configfile))

    def collect_order():
        pass



    def quit_app():
        logger.info('KeyboardInterrupt, quitting!')
        sys.exit()


if __name__ == '__main__':
    main()
