import json
from pathlib import Path

from src.assets.headers import header_small
from src._Modules.meta_data import Metadata, CommandHelp, CommandVersion
from src._Modules.command_registry import CommandRegistry

@CommandRegistry.register
class InfoCommand(Metadata):
    name = 'info'
    aliases = ['--info']

    category = 'Projects'
    description = 'Shows project information'

    version = CommandVersion.DEV
    command_help = CommandHelp(
        syntax='ProgressiveNodeX info [--file <path_to_pnx.json>] [--json]',
        usage='Reads a pnx.json file and displays project information.',
        output='Prints project metadata, runtime, build, serve and scripts info.'
    )

    def run(self):
        pnx_file = self.get_pnx_file()

        if not pnx_file.exists():
            print("No pnx.json found.")
            print()
            print("Try:")
            print(">> ProgressiveNodeX info --file <path_to_pnx.json>")
            return
        
        data = self.load_json(pnx_file)

        if data is None:
            return
        
        if '--json' in self.args:
            print(json.dumps(data, indent=4))
            return
        
        self.print_info(data, pnx_file)
    
    def get_pnx_file(self) -> Path:
        if '--file' in self.args:
            index = self.args.index('--file')

            if index + 1 < len(self.args):
                return Path(self.args[index + 1])
        
        return Path.cwd() / "pnx.json"

    def load_json(self, path: Path) -> dict | None:
        try: 
            return json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            print(f'Invalid JSON file: {path}')
            return None
        except Exception as e:
            print(f'Could not read pnx.json: {e}')
            return None
    
    def print_info(self, data: dict, pnx_file: Path):
        project = data.get("project", {})
        runtime = data.get("runtime", {})
        build = data.get("build", {})
        serve = data.get("serve", {})
        scripts = data.get("scripts", {})
        template = project.get("template_info", {})
        mode = project.get("mode", {})

        print(header_small)
        print()
        print("═══════════════════════════════════════════════════════════════")
        print("Project Information")
        print("═══════════════════════════════════════════════════════════════")
        print()

        self.row("PNX File", str(pnx_file))
        print()

        self.section("Project")
        self.row("Name", project.get("name", "Unknown"))
        self.row("Description", project.get("description", ""))
        self.row("Version", project.get("version", "Unknown"))
        self.row("Author", project.get("author", "Unknown"))
        self.row("License", project.get("license", "Unknown"))
        print()

        self.section("Runtime")
        self.row("Language", runtime.get("language", "Unknown"))
        self.row("Framework", runtime.get("framework", "Unknown"))
        self.row("Entrypoint", runtime.get("entrypoint", "Unknown"))
        print()

        self.section("Template")
        self.row("Used", template.get("template_used", "Unknown"))
        self.row("Name", template.get("template_name", "Unknown"))
        self.row("Version", template.get("template_version", "Unknown"))
        print()

        self.section("Mode")
        self.row("Debug", mode.get("debug", "Unknown"))
        self.row("Development", mode.get("development", "Unknown"))
        self.row("Release", mode.get("release", "Unknown"))
        print()

        self.section("Build")
        self.row("Output", build.get("output", "Unknown"))
        self.row("Targets", ", ".join(build.get("targets", [])))
        print()

        self.section("Serve")
        self.row("Host", serve.get("host", "Unknown"))
        self.row("Port", serve.get("port", "Unknown"))
        self.row("Reload", serve.get("reload", "Unknown"))
        print()

        if scripts:
            self.section("Scripts")

            for name, command in scripts.items():
                self.row(name, command)

            print()
        
        print("═══════════════════════════════════════════════════════════════")

    def section(self, title: str):
        print(title)
        print("─" * len(title))

    def row(self, key: str, value):
        print(f'{key:<14} {value}')