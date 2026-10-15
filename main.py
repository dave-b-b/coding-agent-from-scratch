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
You are an helpful coding agent. When a user asks you to perform an action, you should look to see whether there is a toolcall available and provide the tools and args for that tool call. 
Otherwise provide a normal text response.

The possible tools are:
`read_file`

You must load this into the reponse under the tools param and specify the arg under teh args param. 

If the text does not require a tool, then do not load the tool.

If you have read text from a file, then I want you to read the text as if it is a message from a user.
"""



def command_prompt():
    return ""

def call_llm(prompt: str) -> ChatCompletion:
    return openai_client.chat.completions.create(
        model="gpt-5-nano",
        max_completion_tokens=4000,
        reasoning_effort="low",
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
    choice = response.choices[0]
    if choice.finish_reason == "length" or not choice.message.content:
        print("The model hit its output limit; try a larger token budget.")
        return

    original_content = response.choices[0].message.content
    json_parsed = json.loads(original_content)
    print(f"{ASSISTANT_COLOR}AGENT: {json_parsed["message_content"]}{RESET_COLOR}")

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
            response = call_llm(MASTER_PROMPT)
            choice = response.choices[0]
            if choice.finish_reason == "length" or not choice.message.content:
                print("The model hit its output limit; try a larger token budget.")
                continue
            response_content = response.choices[0].message.content
            response_json = json.loads(response_content)
            response_type = response_json["response_type"]
            tools = response_json["tools"]
            args = response_json["args"]

            add_to_conversation("system", response_content)

            if response_type == "message":
                print_system_response(response)
            elif response_type == "tool_call":
                if tools == "read_file":
                    tool: Tool = get_tool("read_file")
                    print("Reading the  file...")
                    output = tool.function(args["file_name"])
                    text_prompt= "\nHere is the text from the file: " + output
                    print(text_prompt)

                    add_to_conversation("user", text_prompt)

                    read_response = call_llm(MASTER_PROMPT)
                    add_to_conversation("system", text_prompt)
                    print_system_response(read_response)

            # if contains_tool_calls(response):
            #     tool = get_tool(response)
            #     args = get_args(response)
            #     tool.function();
            add_to_conversation(role="system", content=response.choices[0].message.content)
            break


if __name__ == "__main__":
    run_agent()



# Plan 
# I want to build an agent. The agent will have to be able to run in two loops
# It will have to read, list, and open files
# it will have to take actions
# it will have to stay in a loop until I finish with it. 
# It will have to keep track of user prompts and system prompts
