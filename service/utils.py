import uuid
from datetime import datetime, date, timedelta
import decimal
import logging

logging.basicConfig(format='%(asctime)-15s %(name)-15s - %(levelname)-7s : %(message)s', level=logging.DEBUG)


def json_serial(obj_):
    if isinstance(obj_, datetime):
        if obj_.microsecond == 0:
            return obj_.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return obj_.strftime("%Y-%m-%d %H:%M:%S.%f")
    elif isinstance(obj_, date):
        return obj_.strftime("%Y-%m-%d")
    elif isinstance(obj_, timedelta):
        return str(obj_)
    elif isinstance(obj_, uuid.UUID):
        return str(obj_)
    elif isinstance(obj_, decimal.Decimal):
        return str(obj_)
    raise TypeError("Type %s not serializable" % type(obj_))


def get_change(current, previous):
    if current == previous:
        return 100.0
    else:
        return round(((current - previous) / previous) * 100.0, 2)


def to_str(param, default=None):
    if param is not None and param != "":
        result = str(param).strip()
        return result
    else:
        return default


def Ymd_to_date(param):
    if param is not None and param != "":
        return datetime.strptime(param, '%Y-%m-%d')
    else:
        return None
