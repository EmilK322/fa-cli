import typer

from .app import children_app


@children_app.command()
def hello(name: str):
    typer.echo(f"Hello {name}")
