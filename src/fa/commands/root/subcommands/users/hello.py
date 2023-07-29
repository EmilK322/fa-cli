import typer

from .app import users_app


@users_app.command()
def hello(name: str):
    typer.echo(f"Hello {name}")
