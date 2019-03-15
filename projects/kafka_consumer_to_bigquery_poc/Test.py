
import datetime as dt
import time

raw_millis = 1523317852
#raw_millis = 1512585875
date = dt.datetime.fromtimestamp(raw_millis)
print('raw_millis={0}'.format(date))

raw_now = time.time()
raw_now = int('1523317853')
#raw_now = int('152331785')
date = dt.datetime.fromtimestamp(raw_now).isoformat()
print('now={0}'.format(date))
date = dt.datetime.fromtimestamp(raw_now)

raw_now = float('1523317852.949')
date = dt.datetime.fromtimestamp(raw_now)
print('now2={0}'.format(date.strftime("%Y-%m-%d %H:%M:%S.%f")))

#print(dt.datetime.utcfromtimestamp(raw_millis))

