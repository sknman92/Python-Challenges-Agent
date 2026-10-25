# Task 1

from prompt import PIPELINE_EVENTS

from kafka import KafkaProducer

import json
import time


#---------------------------------
# CONSTANTS
sleep_time = 0.5
topic = "pipeline-status"

#---------------------------------
def run_producer(topic:str):
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8"),
    )

    try:
        for p in PIPELINE_EVENTS:
            try:
                key = p['model']
                value = p
                status = value['status']
                producer.send(topic, 
                        key=key,
                        value=value)

                print(f"✅ Sent: {key} | status={status}")

            except Exception as e:
                print(f"❌ Failed to send: {p.get('model')} | {e}")

            time.sleep(sleep_time)

    finally:
        producer.flush()
        producer.close()

if __name__ == "__main__":
    run_producer(topic=topic)