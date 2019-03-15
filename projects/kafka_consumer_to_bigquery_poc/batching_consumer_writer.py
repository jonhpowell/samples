
import time
from confluent_kafka import Consumer, KafkaError

import attribute_extractor
from big_query_streamer import BigQueryStreamer
from time_utils import TimeUtils
from stats_accumulators import StatsAccumulators

# TODO
#
# - tweak message contents
# - make message commit work
# - why don't headers work or we have access? API issue?
# - clean up Kafka JSON extraction
# - main run loop is funky
#


class BatchingConsumerWriter(object):

    def __init__(self, kafka_brokers, bq_dataset, bq_table, max_write_interval, max_batch_size):

        self.bq_dataset = bq_dataset
        self.bq_table = bq_table
        self.max_write_interval = max_write_interval
        self.max_batch_size = max_batch_size
        config = {
            'bootstrap.servers': kafka_brokers,
            'security.protocol': 'ssl',
            'client.id': 'your-client',
            'group.id': 'your-test-group',
            'enable.auto.commit': False,
            'ssl.ca.location': '/<your_path>/client-rpc/ca.pem', # CA certificate file for verifying the broker's certificate.
            'ssl.certificate.location': '/<your_path>/client-rpc/client-rpc.pem',  # client's cert
            'ssl.key.location': '/<your_path>/client-rpc/client-rpc-key.pem',  # client's key
            'ssl.key.password': '<your_ssh_kafka_key>',
            'default.topic.config': {
                'auto.offset.reset': 'earliest'
            }
        }
        self.consumer = Consumer(config)
        print('Started Kafka consumer / BQ writer {}'.format(TimeUtils.now_to_std_time()))

    def consume_messages(self):

        all_stats = StatsAccumulators('all', [TimeUtils.to_minutes(5), TimeUtils.to_hours(1), TimeUtils.to_hours(24)])
#        someco_stats = StatsAccumulators('someco', [TimeUtils.to_minutes(5), TimeUtils.to_hours(1), TimeUtils.to_hours(24)])
        bqs = BigQueryStreamer(self.bq_dataset, self.bq_table)

        self.consumer.subscribe(['maas_notifications'])
        total_msg_count = 0
        last_write_msec = 0
        msg_buffer = []
        while True:
            msg = self.consumer.poll()

            if msg.error():
                code = msg.error().code()
                if code == KafkaError._PARTITION_EOF:
                    continue
                elif code == KafkaError._ASSIGN_PARTITIONS or code == KafkaError._REVOKE_PARTITIONS:
                    print('Revoke/Assign Partition error: {0}'.format(msg.error()))
                    self.consumer.unassign()
                    continue
                else:
                    print(msg.error())
                    break

            #key = msg.key().decode('utf-8')
            msg = msg.value().decode('utf-8')
            all_stats.accumulate(1, len(msg))
            tenant, msg_dict = attribute_extractor.summarize_fields(msg)
            #print('tenant={0}'.format(tenant))
            if True:
#            if 'someco' in tenant:
                total_msg_count += 1
                #print(msg)
                print('{n}: {v}'.format(n=total_msg_count, v=msg_dict))
#                someco.next(1, len(msg))
                msg_buffer.append(msg_dict)
            if (len(msg_buffer) >= self.max_batch_size) or (time.time() - last_write_msec > self.max_write_interval):
                if len(msg_buffer) > 0:
                    bqs.stream_data(msg_buffer)
                    last_write_msec = time.time()
                    msg_buffer.clear()

    def close(self):
        self.consumer.close()


if __name__ == '__main__':

    brokers = "kafka-01.dev.monplat.someco.net:9092,kafka-02.dev.monplat.someco.net:9092,kafka-03.dev.monplat.someco.net:9092"
    bq_dataset = 'realtime_mon'
    bq_table = 'realtime_events'
    write_interval = 5.0   # write at least this often
    max_batch_size = 1000   # NOTE: having update too fast on catch up causes errors (are we exceeding rate limits?)
    consumer_writer = BatchingConsumerWriter(brokers, bq_dataset, bq_table, write_interval, max_batch_size)
    try:
        consumer_writer.consume_messages()
        print('Kafka consumer error; restarting...')
    except Exception as e:
        print(f'Kafka consumer error ({str(brokers)}); quitting...')
    finally:
        consumer_writer.close()
        print(f'Closing Kafka consumer for brokers {brokers}...')

