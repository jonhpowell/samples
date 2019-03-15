
from confluent_kafka import Consumer, KafkaError

import time_utils
import attribute_extractor
from stats_accumulators import StatsAccumulators


# TODO
#
# - tweak message contents
# - make Kafka message commit work
# - why don't headers work or we have access? API issue?
# - clean up Kafka JSON extraction
# - main run loop is funky


class MaasKafkaConsumer(object):

    def __init__(self, kafka_brokers):

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
        print(f'Started Kafka consumer {time_utils.now_to_std_time()}')

    def consume_messages(self):

        all_stats = StatsAccumulators('all', [time_utils.to_minutes(5), time_utils.to_hours(1), time_utils.to_hours(24)])
        somecust_stats = StatsAccumulators('somecust', [time_utils.to_minutes(1), time_utils.to_hours(1), time_utils.to_hours(24)])

        self.consumer.subscribe(['maas_notifications'])
        count = 0
        while True:
            msg = self.consumer.poll()

            if msg.error():
                code = msg.error().code()
                if code == KafkaError._PARTITION_EOF:
                    continue
                elif code == KafkaError._ASSIGN_PARTITIONS or code == KafkaError._REVOKE_PARTITIONS:
                    print(f'Revoke/Assign Partition error: {msg.error()}')
                    self.consumer.unassign()
                    continue
                else:
                    print(msg.error())
                    break

            #key = msg.key().decode('utf-8')
            msg = msg.value().decode('utf-8')
            tenant, msg_dict = attribute_extractor.summarize_fields(msg)
            all_stats.accumulate(1, len(msg))
#            print('tenant={0}'.format(tenant))
#            if 'hybrid:4958307' in tenant:
            if True:
#            if 'somecust' in tenant:
#                somecust_stats.next(1, len(msg))
                count += 1
#                print(msg)
                print('f{count}: {msg_dict}')

    def close(self):
        self.consumer.close()


if __name__ == '__main__':

    brokers = "kafka-01.dev.monplat.somehost.net:9092,kafka-02.dev.monplat.somehost.net:9092,kafka-03.dev.monplat.somehost.net:9092"
    consumer = MaasKafkaConsumer(brokers)
    try:
        consumer.consume_messages()
        print('Kafka consumer error; restarting...')
    except Exception as e:
        print(f'Kafka consumer error ({str(brokers)}); quitting...')
    finally:
        consumer.close()
        print(f'Closing Kafka consumer for brokers {str(brokers)}...')

