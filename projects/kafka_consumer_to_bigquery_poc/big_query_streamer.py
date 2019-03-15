"""
Loads a single row of data directly into BigQuery.
For more information, see the README.rst.
The dataset and table should already exist.
"""

import time
import random
from google.cloud import bigquery
from pprint import pprint
import time_utils


class BigQueryStreamer(object):

    def __init__(self, dataset_id, table_id):

        self.simulate = False
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.client = bigquery.Client()
        dataset_ref = self.client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_id)
        self.table = self.client.get_table(table_ref)

    def stream_data(self, msg_attributes):
        errors = None
        if not self.simulate:
            errors = self.client.insert_rows(self.table, msg_attributes)
        if self.simulate or not errors:
            print(f'Uploaded {len(msg_attributes)} row(s) into BigQuery {self.dataset_id}.{self.table_id}')
        else:
            print('Errors:')
            pprint(errors)

    @staticmethod
    def generate_data(index):
        return {'id': 'raxcloud:'+str(index),
                'tenant_id': '912680',
                'entity': 'ssl-maincal-webserver-' + str(index % 4),
                'timestamp': time_utils.now_to_std_time(),
                'state': 'OK' if (index % 3) else 'Not-OK',
                'status': 'Matched default return statement',
                'alarm': 'Warning (5m > \"2\")'
                }


if __name__ == '__main__':

    dataset = 'realtime_mon'
    table = 'events_no_partition'
    streamer = BigQueryStreamer(dataset, table)

    count = -1
    for iter in range(1, 5):
        rand_size = random.randint(2, 5)
        json_data_arr = []
        for size in range(1, rand_size):
            count += 1
            summary_dict = streamer.generate_data(count)
            print(f'Generating record {count}: {summary_dict}')
            json_data_arr.append(summary_dict)
        streamer.stream_data(json_data_arr)
        time.sleep(0.5)
