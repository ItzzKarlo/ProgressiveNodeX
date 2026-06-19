from src._Modules.command_registry import CommandRegistry
import src.commands_loader

class Commands:
    def __init__(self, args: list[str]):
        self.args = args

    def handle(self):
        if not self.args:
            print("No command given. Use ProgressiveNodeX --help")
            return

        for arg in self.args:
            command_cls = CommandRegistry.find(arg)

            if command_cls:
                command_cls(self.args).run()
                return

        print("Unknown command. Use ProgressiveNodeX --help")