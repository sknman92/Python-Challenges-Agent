import threading
from kafka import KafkaConsumer
import json
import time

#------------------------------------------------------
# VARIABLES
topic = 'pipeline-status'
bootstrap_servers = 'localhost:9092'

def run_consumer(consumer_id: str, group_id: str):

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        consumer_timeout_ms=10000,
        auto_offset_reset='earliest'
    )

    # need to poll, assign, and seek to beginning in case a mis-run
    # while not consumer.assignment():
    #     consumer.poll(timeout_ms=500 0)

    # consumer.seek_to_beginning()

    count = 0

    for message in consumer:
        print(f"  [{consumer_id}] received: {message.value['model']} | status={message.value['status']}")
        count += 1
    
    print(f"  [{consumer_id}] DONE — received {count} total messages")
    consumer.close()

#---------------------------------------------
# SAME GROUP THREADING
# creating threads
consumer_thread_1 = threading.Thread(target=run_consumer, args=('con_1', 'same_group'))
consumer_thread_2 = threading.Thread(target=run_consumer, args=('con_2', 'same_group'))

# starting two threads
consumer_thread_1.start()
consumer_thread_2.start()

# joining two threads
consumer_thread_1.join()
consumer_thread_2.join()

#---------------------------------------------
# DIFFERENT GROUP THREADING
# creating threads
run = int(time.time())
consumer_thread_1 = threading.Thread(target=run_consumer, args=('con_1', f'group_1_{run}'))
consumer_thread_2 = threading.Thread(target=run_consumer, args=('con_2', f'group_2_{run}'))

# starting two threads
consumer_thread_1.start()
consumer_thread_2.start()

# joining two threads
consumer_thread_1.join()
consumer_thread_2.join()

#-------------------------------------
# QUESTIONS
# 1. 8
# 2. 16
# 3. different groups - they would need to receive the same messages
# 4. same group - need to split the events in partitions among them. but would need
    # four paritions to split the work evenly

