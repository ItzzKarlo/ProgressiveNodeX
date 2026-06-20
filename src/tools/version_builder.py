from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
VERSION_FILE = ROOT / "src" / "assets" / "version_info_file.py"

VALID_TYPES = {"DEV", "BETA", "STABLE"}

VERSION_PATTERN = re.compile(
    r'(__version__\s*=\s*)(["\'])(\d{4})\.(\d{2})\.(\d+)(["\'])'
)

TYPE_PATTERN = re.compile(
    r'__type__\s*=\s*(["\'])([^"\']+)\1'
)

def upgrade_version():
    if not VERSION_FILE.exists():
        print(f'Version file not found: {VERSION_FILE}')
        sys.exit(1)
    
    content = VERSION_FILE.read_text(encoding='utf-8')

    version_match = VERSION_PATTERN.search(content)

    if not version_match:
        print('Could not find __version__ in version_info_file.py')
        sys.exit(1)
    
    type_match = TYPE_PATTERN.search(content)

    if not type_match:
        print('Could not find __type__ in version_info_file.py')
        sys.exit(1)
    
    build_type = type_match.group(2)

    if build_type not in VALID_TYPES:
        print(f'Invalid __type__: {build_type}')
        print(f'Allowed values: {",".join(sorted(VALID_TYPES))}')
        sys.exit(1)
    
    old_year = version_match.group(3)
    old_month = version_match.group(4)
    old_build = int(version_match.group(5))

    now = datetime.now()

    new_year = now.year
    new_month = f'{now.month:02d}'
    new_build = old_build + 1

    if new_build > 65535:
        print('Build number is too high for Windows Version metadata.')
        print('Windows file version parts should stay <= 65535.')
        sys.exit(1)
    
    old_version = f'{old_year}.{old_month}.{old_build:04d}'
    new_version = f'{new_year}.{new_month}.{new_build:04d}'

    def replace_version(match):
        return f"{match.group(1)}{match.group(2)}{new_version}{match.group(6)}"
    
    updated_content = VERSION_PATTERN.sub(
        replace_version,
        content,
        count=1
    )

    VERSION_FILE.write_text(updated_content, encoding='utf-8')

    print(f'Version updated: {old_version} -> {new_version}')
    print(f'Build type: {build_type}')

if __name__ == '__main__':
    upgrade_version()