import typer

from .app import parents_app


@parents_app.command()
def hello(name: str):
    typer.echo(f"Hello {name}")
