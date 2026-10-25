from kafka import KafkaConsumer

import json

from collections import Counter

#---------------------------------
# CONSTANTS
sleep_time = 0.5
topic = 'pipeline-status'
bootstrap_servers='localhost:9092'

#---------------------------------
def run_consumer():
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset='earliest',
        consumer_timeout_ms=10000,
        # timeout_ms of 3000 is too short for polling members
        group_id='monitoring-team'
    )

    # join the group and wait until partitions are assigned
    # while not consumer.assignment():
    #   consumer.poll(timeout_ms=5000)

    # # moving kakfa bookmark to the beginning
    # consumer.seek_to_beginning()

    # inititating counter for status
    status_counter = Counter()

    for message in consumer:
        message_value = message.value
        run_id = message_value['run_id']
        status = message_value['status']
        rows = message_value['rows_affected']
        duration_second = message_value['duration_sec']

        model_name = message.key.decode('utf-8')

        if status == 'success':
            status_symbol = "✅"
        elif status == 'warning':
            status_symbol = "⚠️"
        else:
            status = 'failed'
            status_symbol = "❌"    

        print(f"[{run_id}] {model_name} -> {status_symbol} | {rows} | {duration_second}")

        status_counter[status] += 1 

    print(f"""
          --------- Status Summary ---------
          Total processed: {status_counter.total()}
          Successful: {status_counter['success']}
          Warned: {status_counter['warning']}
          Failed: {status_counter['failed']}
          """
          )

    consumer.close()
    
if __name__ == "__main__":
    run_consumer()









