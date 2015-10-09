# -*- coding: utf-8 -*-

import os
import logging
import logging.config
import argparse

from achy.parser import Pain8Doc
from achy.builder import build_pain2
from achy.helpers import timestamp_string

logging.config.fileConfig(os.path.join(os.path.dirname(__file__),'logging.conf'))
logger = logging.getLogger('achy')

def main():
    parser = argparse.ArgumentParser(description='A pain.008 to pain.002 converter.')
    parser.add_argument('-i', '--input-pain8',
                        dest='pain8_file',
                        help='The name of the pain.008 file to parse.')
    parser.add_argument('-v', '--pain8-version',
                        dest='pain8_version',
                        default='pain.008.001.02',
                        help='The pain.008 schema version, defaults to "pain.008.001.02" .')
    parser.add_argument('-o', '--output-pain2',
                        dest='pain2_file',
                        help='The name of the pain.002 file to build.')
    parser.add_argument('-r', '--reasons-file',
                        dest='reasons_file',
                        default=None,
                        help='(Optional) CSV file mapping E2E ID\'s to reason codes.')
    parser.add_argument('-d', '--default-reason',
                        dest='default_reason',
                        default=None,
                        help='(Optional) Default reason code to use if mapping is not supplied.')
    parser.add_argument('-e', '--expanded',
                        dest='expanded',
                        action='store_true',
                        help='Use non-compact (indented) pain.002 template. If missing compact template is used).')

    args = parser.parse_args()

    if args.pain2_file is None:
        args.pain2_file = 'pain.002_' + timestamp_string() + '.xml'

    pain8 = Pain8Doc(args.pain8_file, args.pain8_version)

    pacs2 = build_pain2(pain8, args.reasons_file, args.default_reason, args.expanded)
    with open(args.pain2_file, 'w') as f:
        f.write(pacs2)

if __name__ == '__main__':
    main()
