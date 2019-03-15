
import unittest

import time_utils
from stats_accumulators import StatsAccumulators


class StatsAccumulatorsTest(unittest.TestCase):

    # yeah, this is pretty funky
    def test_overall_functionality(self):
        accums = StatsAccumulators('consumer', [0.5, 1.0, 5.0])
        accums.accumulate(5, 500)
        time_utils.sleep(0.35)
        accums.accumulate(7, 1300)
        time_utils.sleep(0.25)
        accums.accumulate(2, 270)
        time_utils.sleep(0.75)
        actual = accums.report()

        expected = """consumer[0.5 sec]: 2 messages/270 bytes
consumer[1.0 sec]: 14 messages/2K bytes
consumer[5.0 sec]: 14 messages/2K bytes
"""
        self.assertEqual(actual, expected, 'Report should be expected')


if __name__ == '__main__':
    unittest.main()

