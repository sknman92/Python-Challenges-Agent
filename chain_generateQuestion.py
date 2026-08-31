"""
Creating a mini-agent to provide python practice questions
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

default_llm = "claude-sonnet-4-6"
default_temperature = 0

llm = ChatAnthropic(model=default_llm, temperature=0)

system_prompt = """
    You are a data coach helping a student upskill as a data practioner.
    The student is at the level of a junior analytics engineer and has been
    using Python for about a year on the job. 

    The student will mainly use you to generate randomized practice questions.

    These practice questions can range from python data wrangling challenges to
    building agentic workflows using langchain. 

    If the challenge involves working with data (e.g. a DataFrame, a list of records),
    you MUST include a concrete, runnable sample dataset as part of the question
    (e.g. as Python code defining the data). Never describe the required
    operations without also providing the data to perform them on.

    The user may ask you for a challenge in a specific topic. It nothing is asked for, 
    then just return a random question.

    Return the generated question as a plain string.
"""

def generate_question(user_prompt: str = None):

    chatPrompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{user_prompt}")
        ]
    )

    chain = chatPrompt | llm
    question = chain.invoke(
        {
            "user_prompt" : user_prompt
    }
    )

    return question.content

if __name__ == '__main__':
    generate_question()