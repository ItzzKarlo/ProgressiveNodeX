class CommandRegistry:
    commands = []

    @classmethod
    def register(cls, command_cls):
        cls.commands.append(command_cls)
        return command_cls

    @classmethod
    def all(cls):
        return cls.commands

    @classmethod
    def find(cls, arg: str):
        for command_cls in cls.commands:
            if arg == command_cls.name or arg in command_cls.aliases:
                return command_cls

        return None