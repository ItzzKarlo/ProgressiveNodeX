import sys
from src.handle_commands import Commands

def main():
    args = sys.argv[1:]
    Commands(args).handle()

if __name__ == '__main__':
    main()