# -*- coding: utf-8 -*-

import os
import logging
import logging.config
import argparse
import csv
from random import randrange
from jinja2 import Environment, FileSystemLoader

from parser import Pain8Doc

from helpers import iso_datetime, unique_string, timestamp_string

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('achy')

REASON_CODES = [
        'AC01',  # Account identifier incorrect (i.e. invalid IBAN)
        'AC04',  # Account closed
        'AC06',  # Account blocked
        'AG01',  # Direct debit forbidden on this account for regulatory reasons
        'AG02',  # Operation/transaction code incorrect, invalid file format
        'AM04',  # Insufficient funds
        'AM05',  # Duplicate collection
        'BE01',  # Debtor’s name does not match with the account holder's name
        'BE05',  # Identifier of the Creditor Incorrect
        'FF01',  # Operation/transaction code incorrect, invalid file format
        'FF05',  # Direct Debit type incorrect
        'MD01',  # No valid Mandate
        'MD02',  # Mandate data missing or incorrect
        'MD07',  # Debtor deceased
        'MS02',  # Refusal by the Debtor
        'MS03',  # Reason not specified
        'RC01',  # Bank identifier incorrect (i.e. invalid BIC)
        'RR01',  # Missing Debtor Account Or Identification
        'RR02',  # Missing Debtors Name Or Address
        'RR03',  # Missing Creditors Name Or Address
        'RR04',  # Regulatory Reason
        'SL01'   # Specific Service offered by the Debtor Bank
    ]


def render_pacs2(data):
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
    template = env.get_template('pain2.xml')
    return template.render(data=data)


def build_pacs2(data, reasons_file=None):
    # Build dict mapping E2EID's to reason codes, if supplied
    reasons_mapping = {}
    if reasons_file is not None:
        with open(reasons_file) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                reasons_mapping[row[0].strip()] = row[1].strip()

    mapped_e2eids = reasons_mapping.keys()

    if reasons_mapping:
        include_batches = {}
        for batch in data.batches:
            skip_batch = True
            include_collections = []
            for collection in batch.collections:
                if collection.e2e_id in mapped_e2eids:
                    collection['reject_reason'] = reasons_mapping[collection.e2e_id]
                    collection['sts_id'] = unique_string('RJC')
                    include_collections.append(collection.e2e_id)
                    skip_batch = False
            if not skip_batch:
                include_batches[batch.id] = include_collections

        data.batches = [batch for batch in data.batches if batch.id in include_batches]
        for batch in data.batches:
            batch.collections = [coll for coll in batch.collections if coll.e2e_id in include_batches[batch.id]]
    else:
        logger.info('Mapping not provided, using random reason codes')
        for batch in data.batches:
            for collection in batch.collections:
                collection['reject_reason'] = REASON_CODES[randrange(len(REASON_CODES))]
                collection['sts_id'] = 'RJCT' + unique_string('RJC')

    data.orig_msg_id = data.msg_id
    data.orig_tx_count = data.tx_count
    data.orig_sum = data.sum

    data.msg_id = unique_string()
    data.dttm = iso_datetime()

    return render_pacs2(data)


def main():
    parser = argparse.ArgumentParser(description='A pain.008 to pain.002 converter.')
    parser.add_argument('-i', '--input-pain8',
                        dest='pain8_file',
                        help='The name of the pain.008 file to parse')
    parser.add_argument('-o', '--output-pain2',
                        dest='pain2_file',
                        help='The name of the pain.002 file to build')
    parser.add_argument('-r', '--reasons-file',
                        dest='reasons_file',
                        default=None,
                        help='(Optional) CSV file mapping E2E ID\'s to reason codes')
    args = parser.parse_args()

    if args.pain2_file is None:
        args.pain2_file = 'pain.002_' + timestamp_string() + '.xml'

    pain8 = Pain8Doc(args.pain8_file)

    pacs2 = build_pacs2(pain8, args.reasons_file)
    with open(args.pain2_file, 'w') as f:
        f.write(pacs2)

if __name__ == '__main__':
    main()

