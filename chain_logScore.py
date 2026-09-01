"""
Creating a mini-agent to log result of the attempt on challenge
and update progress.md
"""

from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from pydantic import BaseModel

from chain_generateQuestion import generate_question
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic_schema import ScorecardRow
from sql_db import insert_row, select_rows, table_name, py_schema

default_llm = "claude-sonnet-4-6"
default_temperature = 0

llm = ChatAnthropic(model_name=default_llm, temperature=0) 
llm_structured_output = llm.with_structured_output(ScorecardRow)                      

system_prompt = """
    You are storing the result of a student attempting a Python challenge. 

    Retrieve the attempt from the file path provided by the user.

    Grade the attempt from A-D.

    Your grading will be stored as a row in SQL database. 

    Fields required for the row:
        1. Date: {date}
        2. Challenge_Summary
        3. Main_Topic
        4. Score
        5. Feedback 
"""

def _todays_date() -> pd.Timestamp:
    """
    Helper function to generate today's date to pass into system prompt
    """

    today_timestamp = pd.Timestamp.now()
    return today_timestamp

def retrieve_attempt():

    path_attemptFile = input("Input path to your attempt file: ")

    try:
        return Path(path_attemptFile).read_text()
    except Exception as e:
        print(f"Could not open attempt file: {e}")
        raise

def update_progress_md(table_name: str, py_schema: type[BaseModel], path: str = "progress.md"):
      rows = select_rows(table_name, py_schema)

      by_topic = {}
      for row in rows:
          by_topic.setdefault(row["Main_Topic"], Counter())[row["Score"]] += 1

      lines = ["# Progress\n"]
      for topic, counts in by_topic.items():
          breakdown = ", ".join(f"{grade}: {n}" for grade, n in sorted(counts.items()))
          lines.append(f"- **{topic}** — {breakdown}")

      Path(path).write_text("\n".join(lines), encoding="utf-8")

      # practicing counter operations - nested: date -> main_topic -> Counter(score)

      # 1) setdefault version
      by_date = {}
      for row in rows:
          topic_counts = by_date.setdefault(row['Date'], {})
          topic_counts.setdefault(row['Main_Topic'], Counter())[row['Score']] += 1
      print("setdefault:", by_date)

      # 2) same result, without setdefault (manual check-then-create at each level)
      by_date_manual = {}
      for row in rows:
          if row['Date'] not in by_date_manual:
              by_date_manual[row['Date']] = {}
          if row['Main_Topic'] not in by_date_manual[row['Date']]:
              by_date_manual[row['Date']][row['Main_Topic']] = Counter()
          by_date_manual[row['Date']][row['Main_Topic']][row['Score']] += 1
      print("manual:", by_date_manual)

      # 3) same result, using defaultdict instead of setdefault
      by_date_dd = defaultdict(lambda: defaultdict(Counter))
      for row in rows:
          by_date_dd[row['Date']][row['Main_Topic']][row['Score']] += 1
      print("defaultdict:", dict(by_date_dd))
      
def llm_chain():

    chatPrompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{attempt}")
        ]
    )

    return chatPrompt | llm_structured_output

def _store_row(attempt):

    """
    Storing attempt score into sql db
    :param attempt: the student's attempt code, as text
    """

    date = _todays_date()
    row = llm_chain().invoke(
        {
        "date" : date,
        "attempt" : attempt
        }  
        )

    insert_row(row, table_name, py_schema)

def grade_and_log(attempt):
    """
    Public entry point for grading and logging an attempt
    """
    _store_row(attempt)
    update_progress_md(table_name, py_schema)

    return


