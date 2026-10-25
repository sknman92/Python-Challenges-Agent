# `# 🚀 Kafka Fundamentals Challenge: Streaming Pipeline Status Events

# ---

# ## 🧠 What Is Kafka? (Read This First)

# As an analytics engineer, you're used to batch pipelines — dbt runs, scheduled Airflow DAGs, etc. But what happens when you need to react to events *as they happen*? That's where **Apache Kafka** comes in.

# **Kafka is a distributed event streaming platform.** Think of it like a high-throughput, durable message queue where:
# - **Producers** write events (messages) to Kafka
# - **Consumers** read those events from Kafka
# - Events are organized into **Topics** (like named channels or tables)
# - Kafka **retains** messages for a configurable period — consumers can re-read them

# ### 📦 Key Concepts You'll Use Today

# | Concept | Analogy | Description |
# |---|---|---|
# | **Topic** | A database table | A named stream of related events (e.g. `pipeline-status`) |
# | **Producer** | An INSERT statement | Code that writes events to a topic |
# | **Consumer** | A SELECT query | Code that reads events from a topic |
# | **Message/Event** | A row | A single unit of data sent to a topic (has a key + value) |
# | **Consumer Group** | A team of workers | A group of consumers that share the work of reading a topic. Each message goes to only ONE member of the group |
# | **Offset** | A row number | Kafka tracks where each consumer group is up to in a topic |
# | **Broker** | The database server | A single Kafka server that stores and serves messages |
# | **Partition** | A shard | Topics are split into partitions for parallelism. Today we'll use 1 partition to keep it simple |

# ### 🔁 The Core Flow

# ```
# [Producer] --> writes events --> [Kafka Topic] --> read by --> [Consumer(s)]
# ```

# Kafka sits *between* your systems. A pipeline orchestrator could produce events, and a monitoring dashboard could consume them — completely decoupled.

# ---

# ## 🛠️ Setup: Running Kafka Locally

# You'll run Kafka locally using Docker. This is the fastest way to get started.

# ### Step 1: Install Docker Desktop
# If you don't have it: https://www.docker.com/products/docker-desktop

# ### Step 2: Create a `docker-compose.yml` file

# Create a new folder called `kafka-challenge/` and inside it, create this file:

# ```yaml
# # docker-compose.yml
# version: '3.8'
# services:
#   zookeeper:
#     image: confluentinc/cp-zookeeper:7.4.0
#     environment:
#       ZOOKEEPER_CLIENT_PORT: 2181
#       ZOOKEEPER_TICK_TIME: 2000

#   kafka:
#     image: confluentinc/cp-kafka:7.4.0
#     depends_on:
#       - zookeeper
#     ports:
#       - "9092:9092"
#     environment:
#       KAFKA_BROKER_ID: 1
#       KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
#       KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
#       KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
# ```

# > **What's Zookeeper?** It's a coordination service Kafka uses to manage brokers. In newer Kafka versions it's being replaced, but for learning purposes this setup is standard and simple.

# ### Step 3: Start Kafka

# ```bash
# cd kafka-challenge
# docker-compose up -d
# ```

# Wait about 15 seconds for Kafka to fully start. You can verify it's running with:

# ```bash
# docker-compose ps
# ```

# Both `zookeeper` and `kafka` should show as `Up`.

# ### Step 4: Install the Python library

# ```bash
# pip install kafka-python
# ```

# ---

# ## 📁 Your Project Structure

# ```
# kafka-challenge/
# ├── docker-compose.yml
# ├── producer.py
# ├── consumer.py
# └── consumer_group_demo.py
# ```

# ---

# ## 🎯 The Scenario

# You're an analytics engineer at a company with dozens of dbt models running throughout the day. You want to build a lightweight **pipeline monitoring system** using Kafka.

# The idea:
# - A **producer** simulates dbt pipeline runs finishing and emits status events (success, failure, warning) to a Kafka topic called `pipeline-status`
# - A **consumer** reads those events and prints a formatted status report
# - You'll then explore **consumer groups** to understand how Kafka distributes work

# Here is your sample data — a list of pipeline run events your producer will send:

# ```python
# # This is the data your producer will work with
PIPELINE_EVENTS = [
    {"run_id": "run_001", "model": "stg_orders",        "status": "success", "duration_sec": 12, "rows_affected": 5400},
    {"run_id": "run_002", "model": "stg_customers",     "status": "success", "duration_sec": 8,  "rows_affected": 1200},
    {"run_id": "run_003", "model": "int_order_items",   "status": "warning", "duration_sec": 45, "rows_affected": 9800},
    {"run_id": "run_004", "model": "fct_revenue",       "status": "failure", "duration_sec": 3,  "rows_affected": 0},
    {"run_id": "run_005", "model": "dim_products",      "status": "success", "duration_sec": 6,  "rows_affected": 340},
    {"run_id": "run_006", "model": "fct_user_sessions", "status": "success", "duration_sec": 22, "rows_affected": 87600},
    {"run_id": "run_007", "model": "int_payments",      "status": "failure", "duration_sec": 2,  "rows_affected": 0},
    {"run_id": "run_008", "model": "dim_dates",         "status": "success", "duration_sec": 1,  "rows_affected": 365},
]
# ```

# ---

# ## ✅ Your Tasks

# ---

# ### Task 1 — Write the Producer (`producer.py`)

# **Goal:** Send each pipeline event as a Kafka message to the `pipeline-status` topic.

# **Requirements:**
# - Import `KafkaProducer` from `kafka`
# - Connect to Kafka at `localhost:9092`
# - Serialize message values as JSON (hint: use the `value_serializer` parameter — you'll want to encode a dict to JSON bytes)
# - Use the `model` name as the **message key** (hint: use `key_serializer` too — encode the string to bytes)
# - Loop through `PIPELINE_EVENTS` and send each one using `producer.send(topic, key=..., value=...)`
# - Add a `time.sleep(0.5)` between sends to simulate real-time streaming
# - Call `producer.flush()` at the end to ensure all messages are delivered
# - Print a confirmation line for each message sent, e.g.: `✅ Sent: fct_revenue | status=failure`

# **Concepts to understand as you build this:**
# - Why do we serialize to bytes? Kafka messages are raw bytes — it doesn't know about Python dicts or JSON. The serializer is your bridge.
# - Why use a message key? Keys control which **partition** a message goes to. Messages with the same key always go to the same partition — useful for ordering guarantees per model name.

# ---

# ### Task 2 — Write the Consumer (`consumer.py`)

# **Goal:** Read all pipeline events from the `pipeline-status` topic and print a formatted report.

# **Requirements:**
# - Import `KafkaConsumer` from `kafka`
# - Connect to `localhost:9092`, subscribing to `pipeline-status`
# - Deserialize the message value from JSON bytes back to a Python dict (hint: use `value_deserializer`)
# - Set `auto_offset_reset='earliest'` — this tells Kafka to start reading from the **very first message** in the topic, not just new ones. This is important because your producer already ran.
# - Set `consumer_timeout_ms=3000` — this makes the consumer stop waiting for new messages after 3 seconds of silence (so your script exits cleanly instead of waiting forever)
# - Assign this consumer to a **consumer group** called `"monitoring-team"` using the `group_id` parameter
# - For each message received, print a formatted line like:

# ```
# 📨 [run_004] fct_revenue → ❌ FAILURE | 0 rows | 3s
# 📨 [run_001] stg_orders  → ✅ SUCCESS | 5400 rows | 12s
# ```

# Use emojis or symbols to make statuses visually distinct (✅ success, ⚠️ warning, ❌ failure).

# - After consuming all messages, print a summary: total events received, how many were success / warning / failure.

# **Concepts to understand as you build this:**
# - `auto_offset_reset='earliest'`: Kafka tracks *where you left off* per consumer group. If your group has never read this topic before, `earliest` means "start from the beginning." The alternative, `latest`, means "only read new messages from now on."
# - `group_id`: This is how Kafka identifies your consumer group. If you run two consumers with the same `group_id`, Kafka splits the partitions between them.

# ---

# ### Task 3 — Consumer Group Demo (`consumer_group_demo.py`)

# **Goal:** Understand what a consumer group actually does by running two consumers simultaneously.

# **Context:** In a real analytics platform, you might have multiple downstream systems that all need to react to the same pipeline events — e.g. a Slack alerting bot AND a metrics dashboard. Kafka handles this elegantly with consumer groups.

# **The rule:**
# - Two consumers in the **same group** → they *share* the messages (each message goes to only one of them)
# - Two consumers in **different groups** → they each get *all* the messages independently

# **Your task:**

# Write a script that demonstrates this by using Python's `threading` module to run two consumers at the same time.

# **Part A — Same Consumer Group (message sharing):**

# ```python
# import threading
# from kafka import KafkaConsumer
# import json

# def run_consumer(consumer_id: str, group_id: str):
#     consumer = KafkaConsumer(
#         'pipeline-status',
#         bootstrap_servers='localhost:9092',
#         group_id=group_id,
#         auto_offset_reset='earliest',
#         value_deserializer=lambda x: json.loads(x.decode('utf-8')),
#         consumer_timeout_ms=5000
#     )
#     count = 0
#     for message in consumer:
#         print(f"  [{consumer_id}] received: {message.value['model']} | status={message.value['status']}")
#         count += 1
#     print(f"  [{consumer_id}] DONE — received {count} total messages")
#     consumer.close()

# # TODO: Create two threads, both using group_id="shared-group"
# # Run them simultaneously using thread.start() and thread.join()
# # Observe: the 8 messages should be split between the two consumers
# ```

# > ⚠️ **Note:** Since our topic only has 1 partition, Kafka can only assign it to 1 consumer in a group at a time. So in Part A, one consumer will get all 8 messages and the other will get 0. This is expected and is a great learning moment — to truly parallelize, you'd need multiple partitions. The key insight is that Kafka *tries* to distribute partitions across consumers in a group.

# **Part B — Different Consumer Groups (independent reads):**

# ```python
# # TODO: Run the same two threads but give them DIFFERENT group_ids:
# # consumer_1 → group_id="team-alerts"
# # consumer_2 → group_id="team-metrics"
# # Observe: BOTH consumers receive all 8 messages independently
# ```

# **After running both parts, answer these questions in comments in your script:**

# ```python
# # Q1: In Part A (same group), how many total messages did both consumers receive combined?
# # Q2: In Part B (different groups), how many total messages did both consumers receive combined?
# # Q3: Which pattern would you use if you wanted a Slack bot AND a dashboard to both
# #     react to every pipeline failure? Same group or different groups? Why?
# # Q4: Which pattern would you use if you had 1 topic with millions of events and
# #     wanted 4 workers to process them in parallel? Same group or different groups? Why?
# ```

# ---

# ## 🧪 Bonus Challenges (Optional)

# **Bonus 1:** Modify your producer to also send a `timestamp` field (use `datetime.utcnow().isoformat()`) and have your consumer print how old each event is when it's consumed.

# **Bonus 2:** Add a `KafkaAdminClient` to your producer script that programmatically creates the `pipeline-status` topic with 3 partitions before sending messages. Then re-run the consumer group demo — does Part A behave differently now?

# **Bonus 3:** Wrap your `KafkaConsumer` in a Python context manager using a `with` statement (you're already comfortable with these!). Look up whether `KafkaConsumer` supports the context manager protocol natively.

# ---

# ## 🏁 How to Verify You've Got It

# Run your scripts in this order:

# ```bash
# # Terminal 1 — start the consumer first so it's ready
# python consumer.py

# # Terminal 2 — send the events
# python producer.py

# # Watch Terminal 1 print events as they arrive!

# # Then run the group demo
# python consumer_group_demo.py
# ```

# When you're done, shut down Kafka cleanly:

# ```bash
# docker-compose down
# ```

# ---

# ## 💡 Key Takeaways for an Analytics Engineer

# - Kafka is like a **durable, replayable event log** — unlike a queue, messages aren't deleted after being read (until the retention period expires)
# - **Consumer groups** let you build multiple independent downstream consumers from the same event stream — decoupled, scalable
# - The **producer/consumer decoupling** means your dbt pipeline doesn't need to know anything about who's listening — it just emits events


#------------------------------
# SOLUTION

