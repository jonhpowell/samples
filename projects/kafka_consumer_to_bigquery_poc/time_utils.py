# Utility file

import datetime as dt
import time


# GCP wants YYYY-MM-DD HH-MM-SS.SSSSS format (ISO format is close, but no T and want fractional seconds)
def fmt_to_std_time(date_time):
    return date_time.strftime("%Y-%m-%d %H:%M:%S.%f").rstrip('0')


def micro_sec_to_std_time(raw_str_time):
    date_time = dt.datetime.fromtimestamp(int(raw_str_time) / 1E3)
    return fmt_to_std_time(date_time)


def now_to_std_time():
    date_time = dt.datetime.fromtimestamp(time.time())
    return fmt_to_std_time(date_time)


def to_minutes(secs):
    return 60.0 * secs


def to_hours(secs):
    return 60.0 * 60.0 * secs


KILO_UNITS = 1024.0
MEGA_UNITS = KILO_UNITS * KILO_UNITS
GIGA_UNITS = KILO_UNITS * MEGA_UNITS
TERA_UNITS = KILO_UNITS * GIGA_UNITS

def fmt_with_units(count):
    if count > TERA_UNITS:
        return '{}T'.format(round(count/TERA_UNITS))
    elif count > GIGA_UNITS:
        return '{}G'.format(round(count / GIGA_UNITS))
    elif count > MEGA_UNITS:
        return '{}M'.format(round(count / MEGA_UNITS))
    elif count > KILO_UNITS:
        return '{}K'.format(round(count / KILO_UNITS))
    else:
        return '{}'.format(count)


if __name__ == '__main__':

    raw_str_time_micros = '1523317852949'
    print('in: {} out: {}'.format(raw_str_time_micros, micro_sec_to_std_time(raw_str_time_micros)))

    raw_str_time_div = '1523317852.949'
    raw_now = float(raw_str_time_div)
    date = dt.datetime.fromtimestamp(raw_now)
    print('now2={0}'.format(date.strftime("%Y-%m-%d %H:%M:%S.%f")))

    print(now_to_std_time())

    raw_str_time_micros2 = 1523892150348.0
    date = dt.datetime.fromtimestamp(raw_now)
    print('now3={0}'.format(date.strftime("%Y-%m-%d %H:%M:%S.%f")))



