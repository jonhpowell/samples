
import time_utils
import time

# TODO
# 1. superior way to do time_interval arrays is to pass tuple of (value, units) and display value/units in output label


class StatsAccumulators(object):

    def __init__(self, label, intervals_secs):
        self.accumulators = []
        self.intervals_secs = intervals_secs
        for interval in intervals_secs:
            self.accumulators.append(StatsAccumulator(label, interval))

    def accumulate(self, msg_count, byte_count):
        for accum in self.accumulators:
            accum.accumulate(msg_count, byte_count)

    def report(self):
        res = ''
        for accum in self.accumulators:
            res += accum.report() + '\n'
        return res


class StatsAccumulator(object):

    def __init__(self, label, interval_secs):
        self.label = label
        self.interval_secs = interval_secs
        self.count = 0
        self.bytes = 0
        self.last_update_sec = time.time()

    def next(self, msg_count, byte_count):
        now = time.time()
        if now - self.last_update_sec >= self.interval_secs:
            print(f'{time_utils.now_to_std_time()} {self.report()}')
            self.last_update_sec = now  # reset everything if interval exceeded...
            self.count = msg_count
            self.bytes = byte_count
        else:
            self.count += msg_count
            self.bytes += byte_count

    def report(self):
        count = time_utils.fmt_with_units(self.count)
        bytes = time_utils.fmt_with_units(self.bytes)
        return f'{self.label}[{self.interval_secs} sec]: {count} messages/{bytes} bytes'


if __name__ == '__main__':

    start_secs = time.time()

    accums = StatsAccumulators('consumer', [0.5, 1.0, 5.0])
    accums.accumulate(5, 500)
    time.sleep(0.35)
    accums.accumulate(7, 1300)
    time.sleep(0.25)
    accums.accumulate(2, 270)
    time.sleep(0.75)
    print(accums.report())

    elapsed_time = (time.time() - start_secs)
    print('elapsed_time={}'.format(elapsed_time))

