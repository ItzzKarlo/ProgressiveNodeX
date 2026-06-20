import shutil
import subprocess
from pathlib import Path

class DependencyManager:
    def __init__(self, project):
        self.project = project
        self.root_dir = project.root_dir
    
    def install(self):
        language = self.project.language.lower()

        if language in ["python", "py"]:
            return self.install_python()
        
        if language in ["javascript", "javascript/js", "typescript", "node", "js"]:
            return self.install_javascript()
        
        if language in ["csharp", "cs", "c#"]:
            return self.install_csharp()
        
        print(f'Unsupported language for dependency installation: {self.project.language}')
        return False
    
    def install_python(self):
        python_exe = self.find_python_executable()

        if python_exe is None:
            print("Python was not found.")
            print()
            print("Please install Python or create a new Virtual Environment first.")
            return False
        
        requirements = self.root_dir / "requirements.txt"
        pyproject = self.root_dir / "pyproject.toml"

        if requirements.exists():
            return self.run([
                str(python_exe),
                "-m", "pip", "install", "-r",
                str(requirements)
            ])
        
        if pyproject.exists():
            return self.run([
                str(python_exe),
                "-m", "pip", "install", "."
            ])
        
        print("No python dependency file found.")
        print('Expected: requirements.txt or pyproject.toml')
        return False
    
    def find_python_executable(self) -> Path | None:
        possible_paths = [
            self.root_dir / ".venv" / "Scripts" / "python.exe",
            self.root_dir / "venv" / "Scripts" / "python.exe",
            self.root_dir / ".venv" / "bin" / "python",
            self.root_dir / "venv" / "bin" / "python"
        ]

        for path in possible_paths:
            if path.exists():
                return path
            
        system_python = shutil.which("python") or shutil.which("python3")

        if system_python:
            return Path(system_python)
        
        return None
    
    def install_javascript(self):
        package_json = self.root_dir / "package.json"

        if not package_json.exists():
            print('No package.json found.')
            return False
        
        if (self.root_dir / "pnpm-lock.yaml").exists() and shutil.which("pnpm"):
            return self.run(["pnpm", "install"])
        
        if (self.root_dir / "yarn.lock").exists() and shutil.which("yarn"):
            return self.run(["yarn", "install"])
        
        if shutil.which("npm"):
            return self.run(["npm", "install"])
        
        print('No JavaScript package manager found.')
        print('Expected npm, pnpm or yarn.')
        return False
    
    def install_csharp(self):
        if not shutil.which("dotnet"):
            print('.NET SDK was not found.')
            return False
        
        has_project = any(self.root_dir.glob('*.csproj'))
        has_solution = any(self.root_dir.glob('*.sln'))

        if not has_project and not has_solution:
            print('No .csproj or .sln file has been found.')
            return False
        
        return self.run(["dotnet", "restore"])
    
    def run(self, command: list[str]):
        print()
        print('Executing: ')
        print(' '.join(command))
        print()

        try: 
            result = subprocess.run(
                command,
                cwd=self.root_dir
            )

            return result.returncode == 0
        
        except KeyboardInterrupt:
            print('Install cancelled by user.')
            return False
        
        except Exception as e:
            print(f'Failed to install dependencies: {e}')
            return False