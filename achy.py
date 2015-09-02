# -*- coding: utf-8 -*-

import sys
import logging
import logging.config
import configparser
import argparse

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('achy')

def main():
    parser = argparse.ArgumentParser(description='A pain.008 to pain.002 converter.')
    parser.add_argument('-c', '--config', default='achy.conf')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read_file(args.config)
    print(config.sections())

if __name__ == '__main__':
    main()

