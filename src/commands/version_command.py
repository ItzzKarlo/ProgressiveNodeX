from src.assets.version_info_file import __version__, __type__
from src.assets.headers import header_big

from src._Modules.meta_data import Metadata, CommandVersion, CommandHelp
from src._Modules.command_registry import CommandRegistry

@CommandRegistry.register
class VersionCommand(Metadata):
    name = '--version'
    aliases = ['-v', 'version']
    description = 'Shows the app\'s version'
    category = 'Information'
    command_help = CommandHelp(
        syntax="ProgressiveNodeX --version",
        usage="Displays the current application version",
        output="Prints the version number"
    )

    def run(self):
        year, month, build = map(int, __version__.split('.'))

        print()
        print(header_big)
        print()
        print("-" * 120)
        print()
        print(f'Build Year     |   {year}')
        print(f'Build Month    |   {month}')
        print(f'Build Number   |   {build}')
        print(f'Build Type     |   {__type__}')
        print()