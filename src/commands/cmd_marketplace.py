from pathlib import Path

from src._Modules.marketplace_client import MarketplaceApiError, get_template, search_templates, upload_template
from src._Modules.meta_data import CommandHelp, CommandVersion, Metadata
from src._Modules.template_packager import prepare_template_archive
from src._Modules.marketplace_auth import get_access_token
from src._Modules.command_registry import CommandRegistry
from src.assets.headers import header_small

@CommandRegistry.register
class MarketplaceCommand(Metadata):
    name = '--marketplace'
    aliases = ['marketplace']
    description = 'Search, inspect and upload marketplace templates.'
    category = 'Marketplace'
    version = CommandVersion.DEV
    command_help = CommandHelp(
        syntax=(
            "ProgressiveNodeX --marketplace search <template>\n",
            "ProgressiveNodeX --marketplace info <template>\n",
            "ProgressiveNodeX --marketplace add template <path> <template-name>",
        ),
        usage='Uses the ProgressiveNodeX marketplace API.',
        output='Displays marketplace results or uplaods a template archive.'
    )

    def run(self):
        print(header_small)

        subcommand = self.get_arg_after_marketplace()

        if subcommand == 'search':
            self.search()
            return
        
        if subcommand == 'info':
            self.info()
            return
        
        if subcommand == 'add':
            self.add()
            return
        
        self.print_useage()


    def marketplace_index(self) -> int | None:
        for index, arg in enumerate(self.args):
            if arg in [self.name, *self.aliases]:
                return index
        
        return None
    
    def get_arg_after_marketplace(self) -> str | None:
        index = self.marketplace_index()

        if index is None:
            return None
        
        if index + 1 >= len(self.args):
            return None
        
        return self.args[index + 1].lower()
    
    def get_value_after(self, token: str) -> str | None:
        for index, arg in enumerate(self.args):
            if arg == token and index + 1 < len(self.args):
                return self.args[index + 1]
            
        return None
    
    def search(self):
        query = self.get_value_after("search")

        if not query:
            print('Search query is required.')
            print('  Example: ProgressiveNodeX --marketplace search hello-pnx')
            return
        
        try:
            response = search_templates(query)
        except MarketplaceApiError as error:
            print(f'Marketplace search failed: {error}')
            return
        
        results = response.get("results", [])

        if not results:
            print(f'No marketplace templates found for: {query}')
            return
        
        print()
        print(f'Marketplace results for: {query}')
        print('--------------------------------')

        for template in results:
            self.print_template_summary(template)
    
    def info(self):
        template_ref = self.get_value_after('info')

        if not template_ref:
            print('Template name or URL is required.')
            print('  Example: ProgressiveNodeX --marketplace info hello-pnx')
            return
        
        try:
            template = get_template(template_ref)
        except MarketplaceApiError as error:
            print(f'Marketplace lookup failed: {error}')
            return
        
        self.print_template_detail(template)
    
    def add(self):
        token = get_access_token()

        if not token:
            print('You are not logged in.')
            print('  Please login: ProgressiveNodeX --auth login')
            return
        
        try:
            add_index = self.args.index('add')
        except ValueError:
            self.print_upload_usage()
            return
        
        if add_index + 3 > len(self.args):
            self.print_upload_usage()
            return
        
        target_type = self.args[add_index + 1].lower()
        source_path = Path(self.args[add_index + 2])
        template_name = self.args[add_index + 3]

        if target_type != 'template':
            self.print_upload_usage()
            return
        
        created_temp_zip = False
        archive_path = None

        try:
            archive_path, created_temp_zip = prepare_template_archive(source_path)
            uploaded = upload_template(archive_path, template_name, token)
        except ValueError as error:
            print(f'Template package error: {error}')
            return
        except MarketplaceApiError as error:
            print(f'Template upload failed: {error}')
            return
        finally:
            if created_temp_zip and archive_path and archive_path.exists():
                archive_path.unlink()
        
        print()
        print('Template uploaded successfully.')
        print()
        print('-------------------------------')
        self.print_template_detail(uploaded)
    
    def print_template_summary(self, template: dict):
        print()
        print(f"Template:  {template.get('slug')}")
        print(f"Name:      {template.get('display_name')}")
        print(f"Author:    {template.get('uploader_username')}")
        print(f"Language:  {template.get('language')}")
        print(f"Version:   {template.get('version')}")
        print(f"Downloads: {template.get('downloads')}")
        print(f"Tags:      {', '.join(template.get('tags', [])) or '-'}")
    
    def print_template_detail(self, template: dict):
        print()
        print("Marketplace Template")
        print("--------------------")
        print(f"Slug:      {template.get('slug')}")
        print(f"Name:      {template.get('display_name')}")
        print(f"Author:    {template.get('uploader_username')}")
        print(f"Language:  {template.get('language')}")
        print(f"Version:   {template.get('version')}")
        print(f"Downloads: {template.get('downloads')}")
        print(f"Tags:      {', '.join(template.get('tags', [])) or '-'}")
        print()
        print(template.get("description") or "No description.")
    
    def print_upload_usage(self):
        print('Usage:\n  ProgressiveNodeX --marketplace add template <path-to-template-folder-or-zip> <template-name>')
    
    def print_usage(self):
        print()
        print("Marketplace Usage")
        print("-----------------")
        print("  ProgressiveNodeX --marketplace search <template-name-or-url>")
        print("  ProgressiveNodeX --marketplace info <template-name-or-url>")
        print("  ProgressiveNodeX --marketplace add template <path-to-template-folder-or-zip> <template-name>")
        print()
        print("Project init:")
        print("  ProgressiveNodeX init --marketplace <template-name-or-url>")