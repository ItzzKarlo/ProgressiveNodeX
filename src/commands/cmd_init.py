import json
import shutil
import sys
from pathlib import WindowsPath, Path
from pathlib import Path

from src._Modules.meta_data import Metadata, CommandHelp, CommandVersion
from src._Modules.command_registry import CommandRegistry
from src.assets.headers import header_small

@CommandRegistry.register
class InitCommand(Metadata):
    name = "init"
    aliases = ["--init", "--create-project"]
    description = CommandVersion.DEV
    category = 'Projects'
    command_help = CommandHelp(
        syntax="ProgressiveNodeX [init | --init | --create-template-project]",
        usage="Creates a new project using a selected template.",
        output="Generates project files and pnx.json in specified path"
    )

    def run(self):
        print(header_small)

        templates = self.get_all_templates()

        if not templates:
            print("No templates have been found.")
            return
        
        project_name = input("Project name: ").strip()
        if not project_name:
            print("Project name cannot be empty.")
            return
        
        target_root = input(f"Project path [Default: {str(Path.cwd())}]: ").strip()
        if not target_root:
            target_root = str(Path.cwd())
        
        target_root = Path(target_root)
        project_dir = target_root / project_name

        print(f'Project "{project_name}" is going to be created in "{project_dir}".')

        if project_dir.exists():
            print(f'Project "{project_dir}" already exists.')
            return
        
        selected_template = self.choose_template(list(templates.keys()))

        if selected_template is None:
            print("Invalid template selection.")
            return

        template_path = templates[selected_template]

        values = {
            "NAME": project_name,
            "DESCRIPTION": input("Description: ").strip(),
            "LANGUAGE": self.detect_language(selected_template),
            "FRAMEWORK": selected_template,
            "ENTRYPOINT": self.default_entrypoint(selected_template),
            "TEMPLATE_USED": "true",
            "TEMPLATE_NAME": selected_template,
            "TEMPLATE_VERSION": "0.0.1",
            "DEBUG": "true",
            "DEVMODE": "true",
            "RELEASEMODE": "false",
            "TARGETS": "windows",
            "TARGETS_2": "linux",
            "TARGETS_3": "macos",
            "OUTPUT": "dist",
            "HOST": "127.0.0.1",
            "PORT": self.default_port(selected_template),
            "RELOAD": "true"
        }

        shutil.copytree(template_path, project_dir)

        self.replace_placeholders(project_dir, values)
        self.create_pnx_json(project_dir, values)

        print()
        print(f'Created project: {project_dir}')
        print(f'Used template: {selected_template}')
        print()
        print("Navigate to your project path and start coding!")
    
    def resource_path(self, relative_path: str) -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys._MEIPASS) / relative_path

        return Path(__file__).resolve().parents[1] / relative_path

    def get_templates(self, templates_dir: Path) -> list[str]:
        return [
            item.name
            for item in templates_dir.iterdir()
            if item.is_dir()
        ]
    
    def default_entrypoint(self, template: str) -> str:
        if template == 'flask': 
            return "app.py"
        
        if template == 'fastapi':
            return "main.py"
        
        if template in ["vue", "react", "svelte", "electron"]:
            return "package.json"
        
        if template in ["cs-desktop", "csharp-desktop"]:
            return "Program.cs"
        
        return "main"
    
    def default_start_command(self, values: dict[str, str]) -> str:
        framework = values["FRAMEWORK"]
        entrypoint = values["ENTRYPOINT"]

        if framework == "flask":
            return f"python {entrypoint}"

        if framework == "fastapi":
            return f"uvicorn {entrypoint.replace('.py', '')}:app --reload"

        if framework in ["vue", "react", "svelte"]:
            return "npm run dev"

        if framework in ["cs-desktop", "csharp-desktop"]:
            return "dotnet run"

        return f"python {entrypoint}"
    
    def choose_template(self, templates: list[str]) -> str | None:
        print()
        print("Available templates:")
        print()

        for index, template in enumerate(templates, start=1):
            print(f"{index}. {template}")
        
        print()

        choice = input('Choose template number: ').strip()

        if not choice.isdigit():
            return None
        
        index = int(choice) - 1

        if index < 0 or index >= len(templates):
            return None
        
        return templates[index]
    
    def replace_placeholders(self, project_dir: Path, values: dict[str, str]):
        for path in project_dir.rglob("*"):
            if not path.is_file():
                continue

            if self.is_binary_file(path):
                continue

            content = path.read_text(encoding='utf-8')

            for key, value in values.items():
                content = content.replace(f'$${key}$$', str(value))

            path.write_text(content, encoding='utf-8')
    
    def create_pnx_json(self, project_dir: Path, values: dict[str, str]):
        pnx_data = {
            "project": {
                "name": values["NAME"],
                "description": values["DESCRIPTION"],
                "version": "0.0.1",
                "mode": {
                    "debug": True,
                    "development": True,
                    "release": False
                },
                "template_info": {
                    "template_used": True,
                    "template_name": values["TEMPLATE_NAME"],
                    "template_version": values["TEMPLATE_VERSION"]
                }
            },
            "runtime": {
                "language": values["LANGUAGE"],
                "framework": values["FRAMEWORK"],
                "entrypoint": values["ENTRYPOINT"]
            },
            "build": {
                "targets": [
                    values["TARGETS"],
                    values["TARGETS_2"],
                    values["TARGETS_3"]
                ],
                "output": values["OUTPUT"]
            },
            "serve": {
                "host": values["HOST"],
                "port": int(values["PORT"]),
                "reload": True
            },
            "scripts": {
                "start": self.default_start_command(values),
                "test": "python -m pytest",
                "version": "ProgressiveNodeX --version",
                "help": "ProgressiveNodeX --help"
            }
        }

        output_path = project_dir / "pnx.json"
        output_path.write_text(
            json.dumps(pnx_data, indent=4),
            encoding='utf-8'
        )

    def is_binary_file(self, path: Path) -> bool:
        binary_ext = {
            ".png", ".jpg", ".jpeg", ".gif", ".ico",
            ".exe", ".dll", ".so", ".zip", ".tar", ".gz",
            ".pdf", ".woff", ".woff2", ".ttf"
        }

        return path.suffix.lower() in binary_ext
    
    def detect_language(self, template: str) -> str:
        if template in ["flask", "fastapi", "django"]:
            return "python"
        
        if template in ["vue", "react", "svelte", "electron"]:
            return "javascript/js"
        
        if template in ["cs-desktop", "csharp-desktop"]:
            return "csharp"
        
        return "unknown"
    
    def default_port(self, template: str) -> str:
        if template == 'flask':
            return "5000"
        
        if template == 'fastapi': 
            return "8000"
        
        if template in ["vue", "react", "svelte", "electron"]:
            return "5173"
        
        return "3000"
    
    def get_builtin_templates_dir(self) -> Path:
        return self.resource_path("src/templates/apps")


    def get_user_templates_dir(self) -> Path:
        import os

        appdata = os.getenv("APPDATA")

        if appdata:
            return Path(appdata) / "ProgressiveNodeX" / "templates" / "apps"

        return Path.home() / ".progressivenodex" / "templates" / "apps"


    def get_all_templates(self) -> dict[str, Path]:
        template_dirs = [
            self.get_builtin_templates_dir(),
            self.get_user_templates_dir()
        ]

        templates = {}

        for templates_dir in template_dirs:
            if not templates_dir.exists():
                continue

            for item in templates_dir.iterdir():
                if not item.is_dir():
                    continue

                if item.name.startswith("_"):
                    continue

                templates[item.name] = item

        return templates