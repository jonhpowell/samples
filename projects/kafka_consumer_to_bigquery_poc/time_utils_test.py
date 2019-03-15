
import unittest

import time_utils


class UtilsTest(unittest.TestCase):

    def test_micro_sec_to_std_time(self):
        raw_str_time_micros = '1523317852949'
        self.assertEqual('2018-04-09 16:50:52.949', time_utils.micro_sec_to_std_time(raw_str_time_micros))

    def test_now_to_std_time(self):
        print(time_utils.now_to_std_time())
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()

