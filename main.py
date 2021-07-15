import argparse
from icecream import ic, install
# initialize icecream in all dependencies
install()

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from core import Ekartoteka
from utils import Config

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--config',
                        help='Configuration file path',
                        type=str,
                        default='./config.yaml')
    args = parser.parse_args()

    config = Config(args.config)
    ekartoteka = Ekartoteka(config=config)
    ekartoteka.login()
    ekartoteka.get_messages()
    ekartoteka.send_nofifications()
