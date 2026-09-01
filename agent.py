import dotenv
dotenv.load_dotenv()
from langchain_core.tools import tool

from chain_logScore import grade_and_log, retrieve_attempt
from chain_generateQuestion import generate_question
from langchain.agents import create_agent
from sql_db import select_rows, table_name, py_schema
import sys

#-----------------------------------------------------------------
# VARIABLES
#-----------------------------------------------------------------

default_llm = "claude-sonnet-4-6"
default_temperature = 0

#-----------------------------------------------------------------
# TOOLS
#-----------------------------------------------------------------

@tool
def generate_question_tool(user_prompt=None):
    """
    Tool for generating question/challenge based on user prompt.
    If user prompt is none, generate question randomly

    Args:
        user_prompt: optional user message on what kind of challenges they want
    """
    try:
        return generate_question(user_prompt=user_prompt)
    except Exception as e:
        return(f"Error generating question: {e}")

@tool
def retrieve_attempt_tool():
    """
    Tool for retrieving attempt. The user will input file path to attempt.
    This tool reads the content of the file path.
    """
    try:
        return retrieve_attempt()
    except Exception as e:
        return(f"Error retrieving attempt: {e}")

@tool
def grade_and_log_tool(attempt):
    """
    Tool for grading and logging the grade of the attempt
    
    Args:
        attempt: content of the attempt fetched by retrieve_attempt_tool
        
    """
    try:
        grade_and_log(attempt)
        return(f"Successfully graded and logged the attempt")
    except Exception as e:
        return(f"Error grading and logging the attempt: {e}")

@tool
def retrieve_past_attempts_tool():
    """
    Tool for returning past attempts from SQL DB.
    Use case: a user may ask the agent to generate a question
    that is harder than the previous challenge. Use this tool
    to grab information about the previous challenge so that you can
    iterate.

    """

    try:
        return select_rows(table_name, py_schema)
    except Exception as e:
        return(f"Error returning past attempts: {e}")

#-----------------------------------------------------------------
# AGENT
#-----------------------------------------------------------------

# TODO: add a tool to allow agent to re-visit past problems and upgrade grading after correction
pipeline_tools = [generate_question_tool,
                  retrieve_attempt_tool,
                  grade_and_log_tool,
                  retrieve_past_attempts_tool]

system_prompt = """ You are the orchestration layer for a pipeline that

    1) Generates questions/challenges for the student to answer
    2) Waits for the student to attempt the challenge
    3) Fetches the content of the attempt based on user input to file path
    4) Grades and logs the attempt
    5) If necessary, retrieves past attempts from SQL DB log

    ## Rules
    - When you receive a question from generate_question_tool, present it to the
      user COMPLETELY AND VERBATIM. Do not summarize, paraphrase, or omit any
      part of it — especially any code blocks containing sample data. The student
      needs the exact content to complete the challenge.
"""

graph = create_agent(
    model=default_llm,
    tools=pipeline_tools,
    system_prompt=system_prompt
)

starter = input("What do you want to practice? (press Enter for a random question)")
message = starter if starter else "Give me a random practice question"

messages = [("user", message)]

while True:
    result = graph.invoke({"messages" : messages})
    messages = result["messages"]
    last = messages[-1]
    print(f"{last} \n {last.content}")

    if not last.tool_calls:
        user_reply = input(">")
        if user_reply.lower() in ('quit', 'exit'):
            break
        messages.append(("user", user_reply))




    
 