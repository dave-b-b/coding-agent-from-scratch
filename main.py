from tool_registry.simple_tool_registry import Tool, ToolRegistry
from openai import OpenAI
import os
from dotenv import load_dotenv

openai_client = OpenAI(api_key=os.environ[OPENAI_API_KEY])

SIMPLE_TOOL_REGISTRY = ToolRegistry();

# Copied directly from https://www.themodernsoftware.dev
YOU_COLOR = "\u001b[94m"
ASSISTANT_COLOR = "\u001b[93m"
RESET_COLOR = "\u001b[0m"

def get_tool(name: str) -> Tool:
    return SIMPLE_TOOL_REGISTRY.get_tool(name)



def command_prompt():
    return ""

def call_llm(prompt: str):
    print(prompt)
    return




def run_agent():
    #get user prompt
    while True:

        # give user prompt to system , get response, print to screen
        while True:
    return ""


if __name__ == "__main__":
    run_agent()



# Plan 
# I want to build an agent. The agent will have to be able to run in two loops
# It will have to read, list, and open files
# it will have to take actions
# it will have to stay in a loop until I finish with it. 
# It will have to keep track of user prompts and system prompts