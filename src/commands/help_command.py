from collections import defaultdict

from src.assets.headers import header_small
from src._Modules.meta_data import Metadata, CommandHelp, CommandVersion
from src._Modules.command_registry import CommandRegistry

@CommandRegistry.register
class HelpCommand(Metadata):
    name = '--help'
    aliases = ['help', '-h']

    category = 'Information'
    description = 'Show available commands'

    version = CommandVersion.RELEASE
    command_help = CommandHelp(
        syntax='ProgressiveNodeX --help',
        usage='Shows all available commands.',
        output='Displays grouped command overview.'
    )

    def run(self):
        target_command = self.get_target_command()

        if target_command:
            self.print_command_help(target_command)
            return
        
        self.print_overview()
    
    def get_target_command(self):
        help_tokens = [self.name, *self.aliases]

        for arg in self.args:
            if arg in help_tokens:
                continue

            command_cls = CommandRegistry.find(arg)

            if command_cls:
                return command_cls
            
        return None

    def print_overview(self):
        print(header_small)
        print()
        print("═══════════════════════════════════════════════════════════════")
        print("                  ProgressiveNodeX Commands")
        print("═══════════════════════════════════════════════════════════════")
        print()

        grouped = defaultdict(list)

        for command_cls in CommandRegistry.all():
            grouped[command_cls.category].append(command_cls)

        for category, commands in grouped.items():
            print(category)
            print("-" * len(category))

            for command_cls in commands:
                print(f'  {command_cls.name:<15} {command_cls.description}')
            
            print()
        
        print("═══════════════════════════════════════════════════════════════")
        print(f'Total Commands: {len(CommandRegistry.all())}')
    
    def print_command_help(self, command_cls):
        help_info = command_cls.command_help

        print(header_small)
        print()
        print("═══════════════════════════════════════════════════════════════")
        print(f'Command: {command_cls.name}')
        print("═══════════════════════════════════════════════════════════════")
        print()
        print(f'Category: {command_cls.category}')
        print(f'Version: {command_cls.version.value}')
        print()
        print("Description")
        print("───────────")
        print(f'  {command_cls.description}')
        print()

        if help_info:
            print('Syntax')
            print("───────────")
            print(f'  {help_info.syntax}')
            print()
            print("Details")
            print("───────────")
            print(f'  {help_info.usage}')
            print()
            print("Result")
            print("───────────")
            print(f'  {help_info.output}')
            print()