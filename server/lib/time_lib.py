# coding: utf-8

from datetime import datetime, timedelta
import time


def now_timestamp():
    timezone_name = time.tzname
    current_time = datetime.now()

    if timezone_name[0] == 'UTC':
        current_time = current_time.replace().timestamp()
        current_time_converted = datetime.utcfromtimestamp(current_time) + timedelta(hours=+9)
        return current_time_converted

    elif timezone_name[0] == 'JST':
        return current_time


def after90days():
    three_months = 90
    return datetime.now() + timedelta(days=three_months)
