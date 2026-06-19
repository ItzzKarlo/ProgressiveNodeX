from src.assets.headers import header_small
from src._Modules.meta_data import Metadata, CommandVersion, CommandHelp
from src._Modules.command_registry import CommandRegistry

@CommandRegistry.register
class HelpCommand(Metadata):
    name = '--help'
    aliases = ['-h']
    description = "Shows the help menu"
    version = CommandVersion.RELEASE
    command_help = CommandHelp(
        syntax="ProgressiveNodeX --help",
        usage="Displays all available commands",
        output="Prints the help menu"
    )

    def run(self):
        print(header_small)
        print()
        print("[ Command ] [ Version ] [ Usage ] [ Output ]")
        print("-" * 80)

        for command_cls in CommandRegistry.all():
            help_info = command_cls.command_help

            if help_info is None:
                continue

            print(
                f"{command_cls.name} | "
                f"{command_cls.version.value} | "
                f"{help_info.usage} | "
                f"{help_info.output}"
            )