# -*- coding: utf-8 -*-

import sys
import logging
import logging.config
import configparser
import json
import argparse

from parser import Pain8Doc

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('achy')


def main():
    parser = argparse.ArgumentParser(description='A pain.008 to pain.002 converter.')
    parser.add_argument('-c', '--config', default='achy.conf.default')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)
    reason_codes = json.loads(config.get('reason_codes', 'codes'))

    p = Pain8Doc('doc/PAIN008_Sample_Boi.xml')
    print(p)
    print(p.batches)

if __name__ == '__main__':
    main()

