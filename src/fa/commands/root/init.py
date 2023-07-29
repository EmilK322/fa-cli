import json
from pathlib import Path

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

import fa.config as config
from fa import __version__
from .app import root_app


@root_app.command()
def init():
    work_dir_path = Path.cwd()
    fa_config_file_path = work_dir_path / config.FA_CONFIG_FILE_NAME
    if not fa_config_file_path.exists():
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            progress.add_task(description='Generating fa config file...')
            with open(fa_config_file_path, 'w', encoding='utf-8') as f:
                json.dump({'version': __version__}, f, indent=4)
    else:
        print('fa config already exists')
        raise typer.Abort()
    # fa_config_file_path.is_file()
    # print(Path.cwd())
