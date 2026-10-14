from tool_registry.simple_tool_registry import Tool, ToolRegistry
from openai import OpenAI
from openai.types.chat import ChatCompletion
from collections.abc import Callable
import json

import os
from dotenv import load_dotenv

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SIMPLE_TOOL_REGISTRY = ToolRegistry();

def read_file(file_name: str) -> str:
    with open(file_name, "r") as file:
        content = file.read()
        print(content)
        return content

SIMPLE_TOOL_REGISTRY.add_tool("read_file", read_file)

# Copied directly from https://www.themodernsoftware.dev
YOU_COLOR = "\u001b[94m"
ASSISTANT_COLOR = "\u001b[93m"
RESET_COLOR = "\u001b[0m"

CONVERSATION: list[dict[str, str]] = []
def get_tool(name: str) -> Tool:
    return SIMPLE_TOOL_REGISTRY.get_tool(name)

MASTER_PROMPT = """
You are an agent. When a user asks you to perform an action, you should look to see whether there is a toolcall available and provide the tools and args for that tool call. 
Otherwise provide a normal text response.

The possible tools are:
`read_file`

You must load this into the reponse under the tools param and specify the arg under teh args param. 

"""



def command_prompt():
    return ""

def call_llm(prompt: str) -> ChatCompletion:
    return openai_client.chat.completions.create(
        model="gpt-5-nano",
        max_completion_tokens=2000,
        reasoning_effort="medium",
        messages=CONVERSATION,
        response_format={
            "type": "json_schema",
            "json_schema":{
                "name": "dynamic_response",
                "description": "This returns a message, but also tool requests",
                "strict" : True,
                "schema": {
                    "type": "object",
                    "properties": {
                        # type to check what was sent
                        "response_type": {
                            "type": "string",
                            "enum" : ["message", "tool_call"]
                        },
                        # messages
                        "message_content": {
                            "type": ["string", "null"]
                        },
                        # tools
                        "tools" : {
                            "type" : ["string", "null"],
                            "enum": ["read_file", None]
                            },
                        "args": {
                            "type": "object",
                            "properties": {
                                "file_name": {"type": ["string", "null"]}
                            },
                            "required": ["file_name"],
                            "additionalProperties": False
                        }
                    },
                    "additionalProperties": False,
                    "required": ["response_type", "message_content", "tools", "args"]
                },
            }
        }
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

def contains_tool_calls(response: ChatCompletion):
    content = response.choices[0].message.content

def get_tool_args(response: ChatCompletion) -> list:
    return response.choices[0].message.content

def run_agent():
    #get user prompt
    while True:
        user_input = get_user_input()
        add_to_conversation("user", content=user_input)
        # give user prompt to system , get response, save, action on response
        while True:
            response = call_llm(MASTER_PROMPT + user_input)
            response_content = response.choices[0].message.content
            response_json = json.loads(response_content)
            response_type = response_json["response_type"]

            if response_type == "message":
                print("message!")
            elif response_type == "tool":
                print("tool call!")

            message_content = response_json["message_content"]
            tools = response_json["tools"]
            args = response_json["args"]

            print_system_response(response)

            # if contains_tool_calls(response):
            #     tool = get_tool(response)
            #     args = get_args(response)
            #     tool.function();

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
