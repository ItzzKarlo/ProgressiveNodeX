from dataclasses import dataclass
from enum import Enum

class CommandVersion(Enum):
    DEV = "Dev"
    BETA = "Beta"
    RELEASE = "Release"
    NOT_CONTINUED = "Not-Continued"

@dataclass
class CommandHelp:
    syntax: str
    usage: str
    output: str

class Metadata:
    name: str = ""
    description: str = ""
    version: CommandVersion = CommandVersion.DEV
    command_help: CommandHelp | None = None
    aliases: list[str] = []

    def __init__(self, args: list[str] | None = None):
        self.args = args or [] 

    def run(self):
        raise NotImplementedError(f"The command ({Metadata.name}) is not implemented yet. Please implement it before running it.")
    