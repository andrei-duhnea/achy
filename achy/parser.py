from xml.etree import ElementTree
from .helpers import Dotable


class Pain8Doc(object):

    def __init__(self, doc_file=None, ns_ver=None):
        self.ns = {'pain8': 'urn:iso:std:iso:20022:tech:xsd:{}'.format(ns_ver)}
        self.tree = None
        self.root = None
        self.msg_id = None
        self.tx_count = None
        self.sum = None
        self.batches = None
        if doc_file is not None:
            self.parse(doc_file)

    def parse(self, doc_file):
        self.tree = ElementTree.parse(doc_file)
        self.root = self.tree.getroot()
        grp_hdr = self.root.find('pain8:CstmrDrctDbtInitn', self.ns).find('pain8:GrpHdr', self.ns)
        self.msg_id = grp_hdr.find('pain8:MsgId', self.ns).text
        self.tx_count = grp_hdr.find('pain8:NbOfTxs', self.ns).text
        self.sum = grp_hdr.find('pain8:CtrlSum', self.ns).text
        self.batches = self.get_batches()

    def get_batches(self):
        batches = []
        batch_elems = self.root.findall('.//pain8:PmtInf', self.ns)
        for batch in batch_elems:
            batch_id = batch.find('pain8:PmtInfId', self.ns).text
            tx_count = batch.find('pain8:NbOfTxs', self.ns).text
            batch_sum = batch.find('pain8:CtrlSum', self.ns).text
            coll_dt = batch.find('pain8:ReqdColltnDt', self.ns).text
            cdtr_scheme_id = batch.find('./pain8:CdtrSchmeId/pain8:Id/pain8:PrvtId/pain8:Othr/pain8:Id', self.ns).text
            seq_type = batch.find('.//pain8:SeqTp', self.ns).text
            cdtr_name = batch.find('./pain8:Cdtr/pain8:Nm', self.ns).text
            cdtr_iban = batch.find('./pain8:CdtrAcct/pain8:Id/pain8:IBAN', self.ns).text
            collection_elems = batch.findall('.//pain8:DrctDbtTxInf', self.ns)
            collections = [self.parse_collection(coll_elem) for coll_elem in collection_elems]
            batches.append(
                Dotable.parse(
                    {
                        'id': batch_id,
                        'tx_count': tx_count,
                        'sum': batch_sum,
                        'coll_dt': coll_dt,
                        'cdtr_scheme_id': cdtr_scheme_id,
                        'seq_type': seq_type,
                        'cdtr_name': cdtr_name,
                        'cdtr_iban': cdtr_iban,
                        'collections': collections
                    }
                )
            )
        return batches

    def parse_collection(self, coll):
        e2e_id = coll.find('./pain8:PmtId/pain8:EndToEndId', self.ns).text
        amt = coll.find('./pain8:InstdAmt', self.ns).text
        mnd_id = coll.find('./pain8:DrctDbtTx/pain8:MndtRltdInf/pain8:MndtId', self.ns).text
        mnd_sig_dt = coll.find('./pain8:DrctDbtTx/pain8:MndtRltdInf/pain8:DtOfSgntr', self.ns).text
        dbtr_name = coll.find('./pain8:Dbtr/pain8:Nm', self.ns).text
        dbtr_iban = coll.find('./pain8:DbtrAcct/pain8:Id/pain8:IBAN', self.ns).text
        return Dotable(
            {
                'e2e_id': e2e_id,
                'amt': amt,
                'mnd_id': mnd_id,
                'mnd_sig_dt': mnd_sig_dt,
                'dbtr_name': dbtr_name,
                'dbtr_iban': dbtr_iban
            }
        )

    def __str__(self):
        return 'pain.008: MsgId: {}, {} txns, EUR {}'.format(self.msg_id, self.tx_count, self.sum)
