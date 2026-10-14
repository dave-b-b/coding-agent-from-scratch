from tool_registry.simple_tool_registry import Tool, ToolRegistry
from openai import OpenAI
from openai.types.chat import ChatCompletion

import os
from dotenv import load_dotenv

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SIMPLE_TOOL_REGISTRY = ToolRegistry();

# Copied directly from https://www.themodernsoftware.dev
YOU_COLOR = "\u001b[94m"
ASSISTANT_COLOR = "\u001b[93m"
RESET_COLOR = "\u001b[0m"

CONVERSATION: list[dict[str, str]] = []
def get_tool(name: str) -> Tool:
    return SIMPLE_TOOL_REGISTRY.get_tool(name)



def command_prompt():
    return ""

def call_llm(prompt: str) -> ChatCompletion:
    return openai_client.chat.completions.create(
        model="gpt-5-nano",
        max_completion_tokens=2000,
        reasoning_effort="medium",
        messages=CONVERSATION
        # response_format={
        #     "tools": Tool,
        #     "args": str,
        #     "body": str
        # }
    )

def get_user_input() -> dict[str, str]:
    return input(f"{YOU_COLOR}USER: {RESET_COLOR}")

def add_to_conversation(role: str, content: str):
    CONVERSATION.append(
        {
            "role": role,
            "content": content
        })

def print_system_response(response: ChatCompletion):
    print(f"{ASSISTANT_COLOR}AGENT: {response.choices[0].message.content}{RESET_COLOR}")

def run_agent():
    #get user prompt
    while True:
        user_input = get_user_input()
        add_to_conversation("user", content=user_input)
        # give user prompt to system , get response, save, action on response
        while True:
            response = call_llm(user_input)
            print_system_response(response)
            add_to_conversation(role="system", content=response)
            break


if __name__ == "__main__":
    run_agent()



# Plan 
# I want to build an agent. The agent will have to be able to run in two loops
# It will have to read, list, and open files
# it will have to take actions
# it will have to stay in a loop until I finish with it. 
# It will have to keep track of user prompts and system prompts