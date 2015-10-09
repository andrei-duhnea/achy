import uuid
from datetime import datetime
import time


class Dotable(dict):
    __getattr__ = dict.__getitem__

    def __init__(self, d):
        self.update(**dict((k, self.parse(v))
                           for k, v in d.items()))

    @classmethod
    def parse(cls, v):
        if isinstance(v, dict):
            return cls(v)
        elif isinstance(v, list):
            return [cls.parse(i) for i in v]
        else:
            return v


def unique_string(prefix='', length=0):
    if length == 0:
        return prefix + str(uuid.uuid4()).replace('-', '')
    else:
        return prefix + str(uuid.uuid4()).replace('-', '')[0:(length - len(prefix))]


def unique_tenchar():
    return str(int((time.time() + 0.5) * 1000))[-10:]


def iso_datetime(date_obj=None):
    if date_obj is None:
        date_obj = datetime.now()
    return date_obj.strftime("%Y-%m-%dT%H:%M:%S")


def timestamp_string():
    return datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M')