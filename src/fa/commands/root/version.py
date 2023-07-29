from fa import __version__
from .app import root_app


@root_app.command()
def version():
    print(__version__)
