from collections.abc import Callable
class Tool:
    def __init__(self, name: str, function: Callable[..., str]):
        self.name = name
        self.function = function


class ToolRegistry:
    def __init__(self):
        self.tools: dict[str, Tool] = {}

    def get_tool(self, name: str) -> Tool:
        return self.tools[name]

