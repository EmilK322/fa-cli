import typer
import fa.config as config


def create_basic_typer(name: str, **kwargs) -> typer.Typer:
    res_typer = typer.Typer(name=name, **config.DEFAULT_TYPER_OBJECT_CONFIG, **kwargs)
    return res_typer


def create_main_typer(**kwargs) -> typer.Typer:
    return create_basic_typer(name='', **kwargs)
