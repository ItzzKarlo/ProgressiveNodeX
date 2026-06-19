from pathlib import Path
import shutil

from src._Modules.meta_data import Metadata, CommandVersion, CommandHelp
from src._Modules.command_registry import CommandRegistry
from src.tools.path_helper import get_user_templates_dir
from src.assets.headers import header_small

@CommandRegistry.register
class CreateCommand(Metadata):
    name = "create"
    aliases = ["--create-template"]
    description = "Creates a new project template."
    category = 'Templates'
    version = CommandVersion.DEV
    command_help = CommandHelp(
        syntax='ProgressiveNodeX create',
        usage='Creates a reuseable template from a folder.',
        output='Adds a new template to the user tempalte directory.'
    )

    def run(self):
        print(header_small)

        template_name = input('Template name: ').strip()
        if not template_name:
            print('Template name cannot be empty.')
            return
        
        source_path = input('Path to existing project/folder: ').strip()
        if not source_path:
            print('Source path may not be empty.')
            return
        
        source_path = Path(source_path)
        if not source_path.exists() or not source_path.is_dir():
            print('Source folder does not exist.')
            return
        
        templates_dir = get_user_templates_dir()
        templates_dir.mkdir(parents=True,exist_ok=True)

        target_path = templates_dir / template_name

        if target_path.exists():
            print(f'Template already exists: {template_name}')
            return
        
        shutil.copytree(
            source_path,
            target_path,
            ignore=shutil.ignore_patterns(
                "__pycache__",
                ".git",
                ".venv",
                "venv",
                ".env"
                "env",
                "node_modules",
                "dist",
                "build",
                "_Out",
                ".idea",
                ".vscode"
            )
        )

        self.create_template_info(target_path, template_name)

        print()
        print(f'Template created: {template_name}')
        print(f'Stored at: {target_path}')
        print()
        print('Create a new project with it using: ')
        print('>> ProgressiveNodeX init')
        print()
    
    def create_template_info(self, target_path: Path, template_name: str):
        info_path = target_path / "template.json"

        content = f"""{{
    "name": "{template_name}",
    "version": "0.0.1",
    "description": "User-created template",
    "created_by": "ProgressiveNodeX",
    "language": "unknown",
    "framework": "custom",
    "entrypoint": "main"
}}
"""

        info_path.write_text(content, encoding="utf-8") 