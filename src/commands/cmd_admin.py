from src._Modules.command_registry import CommandRegistry
from src._Modules.marketplace_auth import get_access_token
from src._Modules.marketplace_client import (
    MarketplaceApiError,
    delete_marketplace_template,
    rename_marketplace_template,
)
from src._Modules.meta_data import Metadata, CommandHelp, CommandVersion
from src.assets.headers import header_small


@CommandRegistry.register
class AdminCommand(Metadata):
    name = '/admin'
    aliases = ["admin", "--admin"]
    description = 'Admin marketplace management commands.'
    version = CommandVersion.DEV
    command_help = CommandHelp(
        syntax=(
            "ProgressiveNodeX /admin --marketplace delete <template>\n",
            "ProgressiveNodeX /admin --marketplace rename <template> <new-template-name>"
        ),
        usage='Requires an admin marketplace account.',
        output='Deletes or renames a marketplace template.'
    )

    def run(self):
        print(header_small)

        if '--marketplace' not in self.args and 'marketplace' not in self.args:
            self.print_usage()
            return
        
        token = get_access_token()

        if not token:
            print('You are not logged in.')
            print('  Please login: ProgressiveNodeX --auth login')
            return
        
        action = self.get_arg_after_marketplace()

        if action == 'delete':
            self.delete(token)
            return
        
        if action == 'rename':
            self.rename(token)
            return
        
        self.print_usage()

    def marketplace_index(self) -> int | None:
        for index, arg in enumerate(self.args):
            if arg in ['--marketplace', 'marketplace']:
                return index
        
        return None
    
    def get_arg_after_marketplace(self) -> str | None:
        index = self.marketplace_index()

        if index is None or index + 1 >= len(self.args):
            return None
        
        return self.args[index + 1].lower()
    
    def delete(self, token: str):
        index = self.marketplace_index()

        if index is None or index + 2 >= len(self.args):
            self.print_usage()
            return
        
        template_ref = self.args[index + 2]

        try:
            response = delete_marketplace_template(template_ref, token)
        except MarketplaceApiError as error:
            print(f'Template delete failed: {error}')
            return
        
        print()
        print(f'Template successfully deleted: {response.get('slug', template_ref)}')
    
    def rename(self, token: str):
        index = self.marketplace_index()

        if index is None or index + 3 >= len(self.args):
            self.print_usage()
            return
        
        template_ref = self.args[index + 2]
        new_template_name = self.args[index + 3]

        try: 
            template = rename_marketplace_template(
                template_ref,
                new_template_name,
                token,
            )
        except MarketplaceApiError as error:
            print(f'Template rename failed: {error}')
            return
    
    def print_usage(self):
        print()
        print('Admin Marketplace Usage')
        print('-----------------------')
        print("  ProgressiveNodeX /admin --marketplace delete <template-name-or-url>")
        print("  ProgressiveNodeX /admin --marketplace rename <template-name-or-url> <new-template-name>")