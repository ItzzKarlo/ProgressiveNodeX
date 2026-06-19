from src._Modules.command_registry import CommandRegistry
from src.commands.help_command import HelpCommand
import src.commands_loader

class Commands:
    def __init__(self, args: list[str]):
        self.args = args

    def handle(self):
        if not self.args:
            CommandRegistry.find("--help")(self.args).run()
            return

        if "--help" in self.args or "-h" in self.args:
            HelpCommand(self.args).run()
            return

        for arg in self.args:
            command_cls = CommandRegistry.find(arg)

            if command_cls:
                command_cls(self.args).run()
                return

        print("Unknown command. Use ProgressiveNodeX --help")