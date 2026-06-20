import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from src._Modules.meta_data import Metadata, CommandHelp, CommandVersion
from src._Modules.command_registry import CommandRegistry
from src._Modules.marketplace_client import MarketplaceApiError, download_template, get_template
from src.assets.headers import header_small

@CommandRegistry.register
class InitCommand(Metadata):
    name = "init"
    aliases = ["--init", "--create-project"]
    description = 'Initializes a new project using an local or marketplace template.'
    version = CommandVersion.DEV
    category = 'Projects'
    command_help = CommandHelp(
        syntax="ProgressiveNodeX [init | --init | --create-template-project]",
        usage="Creates a new project using a selected template.",
        output="Generates project files and pnx.json in specified path"
    )

    def run(self):
        print(header_small)

        if "--marketplace" in self.args or "marketplace" in self.args:
            self.run_marketplace_init()
            return

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
    

    def run_marketplace_init(self):
        template_ref = self.get_marketplace_template_ref()

        if not template_ref:
            print("Marketplace template name or URL is required.")
            print("Example: ProgressiveNodeX init --marketplace hello-pnx")
            return

        try:
            template_info = get_template(template_ref)
        except MarketplaceApiError as error:
            print(f"Marketplace lookup failed: {error}")
            return

        default_project_name = template_info.get("slug") or "pnx-project"

        project_name = input(f"Project name [{default_project_name}]: ").strip()
        if not project_name:
            project_name = default_project_name

        target_root = input(f"Project path [Default: {str(Path.cwd())}]: ").strip()
        if not target_root:
            target_root = str(Path.cwd())

        target_root = Path(target_root)
        project_dir = target_root / project_name

        print(f'Project "{project_name}" is going to be created in "{project_dir}".')

        if project_dir.exists():
            print(f'Project "{project_dir}" already exists.')
            return

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                archive_path = Path(temp_dir) / f"{default_project_name}.zip"
                download_template(template_ref, archive_path)

                manifest = self.read_template_manifest_from_zip(archive_path)

                project_dir.mkdir(parents=True, exist_ok=False)
                self.safe_extract_zip(archive_path, project_dir)

        except MarketplaceApiError as error:
            print(f"Marketplace download failed: {error}")
            return
        except Exception as error:
            if project_dir.exists():
                shutil.rmtree(project_dir, ignore_errors=True)

            print(f"Failed to initialize marketplace template: {error}")
            return

        values = {
            "NAME": project_name,
            "DESCRIPTION": input("Description: ").strip(),
            "LANGUAGE": str(manifest.get("language") or template_info.get("language") or "unknown").lower(),
            "FRAMEWORK": str(manifest.get("framework") or template_info.get("slug") or "marketplace"),
            "ENTRYPOINT": self.detect_entrypoint(project_dir, manifest),
            "TEMPLATE_USED": "true",
            "TEMPLATE_NAME": str(template_info.get("slug") or template_ref),
            "TEMPLATE_VERSION": str(template_info.get("version") or manifest.get("version") or "1.0.0"),
            "DEBUG": "true",
            "DEVMODE": "true",
            "RELEASEMODE": "false",
            "TARGETS": "windows",
            "TARGETS_2": "linux",
            "TARGETS_3": "macos",
            "OUTPUT": "dist",
            "HOST": "127.0.0.1",
            "PORT": self.default_port(str(manifest.get("framework") or "marketplace")),
            "RELOAD": "true"
        }

        self.replace_placeholders(project_dir, values)
        self.create_pnx_json(project_dir, values)

        template_manifest_path = project_dir / "pnx.template.json"
        if template_manifest_path.exists():
            template_manifest_path.unlink()

        print()
        print(f'Created project: {project_dir}')
        print(f'Used marketplace template: {template_info.get("slug")}')
        print()
        print("Navigate to your project path and start coding!")

    def get_marketplace_template_ref(self) -> str | None:
        for index, arg in enumerate(self.args):
            if arg in ["--marketplace", "marketplace"]:
                if index + 1 < len(self.args):
                    return self.args[index + 1]

        return None

    def read_template_manifest_from_zip(self, archive_path: Path) -> dict:
        with zipfile.ZipFile(archive_path, "r") as archive:
            if "pnx.template.json" not in archive.namelist():
                return {}

            raw = archive.read("pnx.template.json").decode("utf-8")
            return json.loads(raw)

    def safe_extract_zip(self, archive_path: Path, target_dir: Path):
        target_dir = target_dir.resolve()

        with zipfile.ZipFile(archive_path, "r") as archive:
            for member in archive.infolist():
                destination = (target_dir / member.filename).resolve()

                try:
                    destination.relative_to(target_dir)
                except ValueError:
                    raise ValueError(f"Unsafe file path in template archive: {member.filename}")

            archive.extractall(target_dir)

    def detect_entrypoint(self, project_dir: Path, manifest: dict) -> str:
        manifest_entry = manifest.get("entrypoint") or manifest.get("entry")

        if isinstance(manifest_entry, str) and manifest_entry.strip():
            return manifest_entry.strip()

        candidates = [
            "main.py",
            "app.py",
            "server.py",
            "index.js",
            "main.js",
            "package.json",
            "Program.cs",
        ]

        for candidate in candidates:
            if (project_dir / candidate).exists():
                return candidate

        return "main"


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