import subprocess
from pathlib import Path

from src.assets.headers import header_small
from src._Modules.meta_data import Metadata, CommandHelp, CommandVersion
from src._Modules.command_registry import CommandRegistry
from src._Modules.project import Project


@CommandRegistry.register
class RunCommand(Metadata):
    name = "run"
    aliases = ["--run"]

    category = "Projects"
    description = "Run the current project"

    version = CommandVersion.DEV
    command_help = CommandHelp(
        syntax="ProgressiveNodeX run [--file <pnx.json>] [--script <name>] [--dry-run] [--debug]",
        usage="Runs a project using the scripts section from pnx.json.",
        output="Executes the selected script inside the project directory."
    )

    def __init__(self, args: list[str] | None = None):
        self.args = args or []

    def run(self):
        try:
            project = self.load_project()
        except Exception as error:
            print(f"Could not load project: {error}")
            return

        if "--list-scripts" in self.args:
            self.list_scripts(project)
            return

        script_name = self.get_script_name()
        command = project.get_script(script_name)

        if not command:
            print(f'Script "{script_name}" was not found in pnx.json.')
            print()
            print("Available scripts:")

            for name in project.scripts:
                print(f"  - {name}")

            return

        self.print_run_info(project, script_name, command)

        if "--dry-run" in self.args:
            return

        self.execute(command, project.root_dir)

    def load_project(self) -> Project:
        if "--file" in self.args:
            index = self.args.index("--file")

            if index + 1 >= len(self.args):
                raise ValueError("--file requires a path to pnx.json")

            return Project.load(Path(self.args[index + 1]))

        return Project.load()

    def get_script_name(self) -> str:
        if "--script" in self.args:
            index = self.args.index("--script")

            if index + 1 < len(self.args):
                return self.args[index + 1]

        return "start"

    def print_run_info(self, project: Project, script_name: str, command: str):
        print(header_small)
        print()
        print("═══════════════════════════════════════════════════════════════")
        print("Running Project")
        print("═══════════════════════════════════════════════════════════════")
        print()
        print(f"Project      {project.name}")
        print(f"Version      {project.version}")
        print(f"Framework    {project.framework}")
        print(f"Language     {project.language}")
        print(f"Script       {script_name}")
        print(f"Directory    {project.root_dir}")
        print()
        print("Command")
        print("───────")
        print(f"  {command}")
        print()
        print("═══════════════════════════════════════════════════════════════")
        print()

    def execute(self, command: str, cwd: Path):
        if "--debug" in self.args:
            print(f"[DEBUG] cwd: {cwd}")
            print(f"[DEBUG] command: {command}")
            print()

        try:
            subprocess.run(
                command,
                shell=True,
                cwd=cwd
            )
        except KeyboardInterrupt:
            print()
            print("Process stopped by user.")
        except Exception as error:
            print(f"Failed to run project: {error}")

    def list_scripts(self, project: Project):
        print(header_small)
        print()
        print("Available Scripts")
        print("═══════════════════════════════════════════════════════════════")
        print()

        if not project.scripts:
            print("No scripts found in pnx.json.")
            return

        for name, command in project.scripts.items():
            print(f"{name:<12} {command}")

        print()
        print("═══════════════════════════════════════════════════════════════")