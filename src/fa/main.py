from fa.utils.command_hierarchy_utils import CommandsAutoRegister


app, _ = CommandsAutoRegister.auto_register()

if __name__ == "__main__":
    app()
    pass


