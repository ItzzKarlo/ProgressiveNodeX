from pathlib import Path

from src._Modules.meta_data import Metadata, CommandHelp, CommandVersion
from src._Modules.dependency_manager import DependencyManager
from src._Modules.command_registry import CommandRegistry
from src.assets.headers import header_small
from src._Modules.project import Project

@CommandRegistry.register
class InstallCommand(Metadata):
    name = 'install'
    aliases = ['--install']

    category = 'Projects'
    description = 'Install project dependencies'

    version = CommandVersion.DEV
    command_help = CommandHelp(
        syntax='ProgressiveNodeX isntall [--file <path_to_pnx.json>]',
        usage='Installs dependencies for current PNX project.',
        output='Runs pip, npm, pnpm, yarn or dotnet restore depending on PNX project type.'
    )

    def __init__(self, args: list[str] | None = None):
        self.args = args or []

    def run(self):
        print(header_small)
        print()
        print("═══════════════════════════════════════════════════════════════")
        print("Install Dependencies")
        print("═══════════════════════════════════════════════════════════════")

        try: 
            project = self.load_project()
        except Exception as e:
            print(f'Could not load project: {e}')
            return
        
        manager = DependencyManager(project)

        print()
        print(f'Project      {project.name}')
        print(f'Language     {project.language}')
        print(f'Framework    {project.framework}')
        print(f'Directory    {project.root_dir}')
        if project.language in ['python', 'py']:
            print(f'Python Int   {manager.find_python_executable()}')
        print()

        success = manager.install()


        print()
        print("═══════════════════════════════════════════════════════════════")

        if success: 
            print('Dependencies installed successfully.')
        else:
            print('Dependency intallation failed or nothing was installed.')
        
        print("═══════════════════════════════════════════════════════════════")

    def load_project(self) -> Project:
        if '--file' in self.args:
            index = self.args.index('--file')

            if index + 1 >= len(self.args):
                raise ValueError('--file requires a path to pnx.json')
            
            return Project.load(Path(self.args[index + 1]))
        
        return Project.load()