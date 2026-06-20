from getpass import getpass

from src._Modules.command_registry import CommandRegistry
from src._Modules.marketplace_auth import clear_auth, get_access_token, get_auth_file, save_auth
from src._Modules.marketplace_client import MarketplaceApiError, get_me, login
from src._Modules.meta_data import CommandHelp, CommandVersion, Metadata
from src.assets.headers import header_small

@CommandRegistry.register
class AuthCommand(Metadata):
    name = 'auth'
    aliases = ['--auth', '/a']
    description = 'Login, logout and inspect marketplace authentication.'
    category = 'Marketplace'
    version = CommandVersion.DEV
    command_help = CommandHelp(
        syntax='ProgressiveNodeX auth [login | logout | whoami]',
        usage='Manages the local ProgressiveNodeX marketplace login session.',
        output='Stores or clears a marketplace access token for API requests.'
    )

    def run(self):
        subcommand = self.get_subcommand()

        if subcommand == 'login':
            self.login()
            return
        
        if subcommand == 'logout':
            self.logout()
            return
        
        if subcommand == 'whoami':
            self.whoami()
            return
        
        self.print_usage()
    
    def get_subcommand(self) -> str | None:
        for index, arg in enumerate(self.args):
            if arg in [self.name, *self.aliases]:
                if index + 1 < len(self.args):
                    return self.args[index + 1].lower()
        
        return None
    
    def login(self):
        print(header_small)
        print()
        print('Marketplace Login')
        print('-----------------')
        print()

        username_or_email = input('Enter your username or email: ').strip()
        password = getpass('Enter your password: ')

        if not username_or_email or not password:
            print('Username/email and password are required.')
            return
        
        try:
            response = login(username_or_email, password)
        
        except MarketplaceApiError as error:
            print(f'Login failed: {error}')
            return
        
        access_token = response.get('access_token')
        user = response.get('user', {})

        if not access_token:
            print('Login failed: API did not return an access token.')
            return
        
        save_auth(
            access_token=access_token,
            username=user.get("username"),
        )

        print()
        print(f'Logged in as: {user.get("username", "unknown")}')
        print(f'Auth saved to: {get_auth_file()}')
    
    def logout(self):
        clear_auth()
        print('Successfully logged out of ProgressiveNodeX marketplace.')
    
    def whoami(self):
        token = get_access_token()

        if not token:
            print('You are currently not logged in.')
            print('Run: ProgressiveNodeX --auth login')
            return
        
        try: 
            user = get_me(token)
        except MarketplaceApiError as error:
            print(f'Couild not verify login: {error}')
            return
        
        print()
        print('Marketplace Account')
        print('-------------------')
        print(f'Username:  {user.get("username")}')
        print(f'Email:     {user.get("email")}')
        print(f'Active:    {user.get("is_active")}')
    
    def print_usage(self):
        print('Usage:')
        print('  ProgressiveNodeX --auth login')
        print('  ProgressiveNodeX --auth whoami')
        print('  ProgressiveNodeX --auth logout')