import typer
# from .subcommands import children
from fa.utils.typer_utils import create_basic_typer

parents_app: typer.Typer = create_basic_typer('parents')
# parents_app.add_typer(children.children_app)
