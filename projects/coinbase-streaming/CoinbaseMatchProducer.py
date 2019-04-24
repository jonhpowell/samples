#!/usr/bin/env python3
import asyncio
import cbpro
from kafka import KafkaProducer
import json
from copra.websocket import Channel, Client


# Get supported products off the Coinbase API
def get_all_products():

    public_client = cbpro.PublicClient()
    prods = []
    for prod in public_client.get_products():
        prods.append(prod['id'])
    return prods


# helper function to trim message to only what's needed
extract = lambda x, y: dict(zip(x, map(y.get, x)))

# event handler for new Coinbase match (extract fields & push to Kafka topic)
class Matches(Client):
    def on_message(self, message):
        if message['type'] == 'match' and 'time' in message:
            md = extract(['trade_id', 'time', 'product_id', 'price', 'size'], message)
            producer.send('coinbase_matches', md)
            print(md)


# main flow

products = get_all_products()
print(f'Getting matches for products {products}')

producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))

loop = asyncio.get_event_loop()
channel = Channel('matches', products)
matches = Matches(loop, channel)
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(matches.close())
    loop.close()

