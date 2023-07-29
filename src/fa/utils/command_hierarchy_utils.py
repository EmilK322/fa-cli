import dataclasses
import importlib
import inspect
import pkgutil
from types import ModuleType

import typer
from rich import print


class CommandHierarchyError(Exception):
    pass


class AppFileError(Exception):
    def __init__(self, message: str, file_path: str):
        super().__init__(message)
        self.message = message
        self.file_path = file_path


class AppFileHasManyTyperAppsError(AppFileError):
    def __init__(self, file_path: str):
        message = f'File {file_path} has more than a single Typer app.'
        super().__init__(message, file_path)


class AppFileHasNoTyperAppError(AppFileError):
    def __init__(self, file_path: str):
        message = f'File {file_path} has no Typer app.'
        super().__init__(message, file_path)


@dataclasses.dataclass
class TyperAppModuleMember:
    name: str
    obj: typer.Typer

    @classmethod
    def from_module(cls, module: ModuleType) -> list['TyperAppModuleMember']:
        name_obj_list: list[tuple[str, typer.Typer]] = inspect.getmembers(module, lambda member: isinstance(member, typer.Typer))
        return [cls(name=name, obj=obj) for name, obj in name_obj_list]


@dataclasses.dataclass
class AppFileModule:
    module: ModuleType
    typer_app: TyperAppModuleMember

    @classmethod
    def from_full_app_file_name(cls, app_file_name: str) -> 'AppFileModule':
        app_file_module: ModuleType = importlib.import_module(app_file_name)
        typer_app_member: TyperAppModuleMember = AppFileModule.get_typer_app_in_app_file(app_file_module)
        return cls(module=app_file_module, typer_app=typer_app_member)

    @staticmethod
    def get_typer_app_in_app_file(app_file_module: ModuleType) -> TyperAppModuleMember:
        typer_app_members: list[TyperAppModuleMember] = TyperAppModuleMember.from_module(app_file_module)
        typer_app_objects: set[typer.Typer] = {member.obj for member in typer_app_members}
        if len(typer_app_objects) > 1:
            raise AppFileHasManyTyperAppsError(app_file_module.__file__)
        if len(typer_app_objects) < 1:
            raise AppFileHasNoTyperAppError(app_file_module.__file__)
        return typer_app_members[0]


class CommandsAutoRegister:
    @staticmethod
    def auto_register(root_command_package: str = 'fa.commands', verbose: bool = False) -> tuple[typer.Typer, dict[str, AppFileModule]]:
        package_to_app_file_map: dict[str, AppFileModule] = CommandsAutoRegister.register_package_commands(package=root_command_package,
                                                                                                           recursive=True, verbose=verbose)
        # because of the command hierarchy, walking on packages from top to bottom so the first is the root
        root_app_file: AppFileModule = list(package_to_app_file_map.values())[0]
        root_command: typer.Typer = root_app_file.typer_app.obj
        return root_command, package_to_app_file_map

    @staticmethod
    def register_package_commands(package: str | ModuleType, parent_app: typer.Typer | None = None, recursive: bool = True, verbose: bool = False) -> dict[str, AppFileModule]:
        if isinstance(package, str):
            try:
                package = importlib.import_module(package)
            except ModuleNotFoundError:
                return {}
        results = {}
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
            sub_package_name = f'{package.__name__}.{name}'
            app_file_name = f'{sub_package_name}.app'
            sub_package_subcommands_package_name = f'{sub_package_name}.subcommands'
            try:
                app_file: AppFileModule = CommandsAutoRegister.get_typer_app_from_file(app_file_name)
            except ModuleNotFoundError:
                continue
            CommandsAutoRegister._save_typer_app(app_file, parent_app, results, sub_package_name, verbose=verbose)

            if recursive and is_pkg:
                results.update(CommandsAutoRegister.register_package_commands(sub_package_subcommands_package_name,
                                                                              parent_app=app_file.typer_app.obj,
                                                                              verbose=verbose))
        return results

    @staticmethod
    def _save_typer_app(app_file: AppFileModule, parent_app: typer.Typer | None, results: dict[str, AppFileModule],
                        sub_package_name: str, verbose: bool = False):
        results[sub_package_name] = app_file
        if verbose:
            print(f'Found {app_file.typer_app.name} with id {id(app_file.typer_app.obj)} from {app_file.module} in {sub_package_name}')
        if parent_app:
            parent_app.add_typer(app_file.typer_app.obj)
            if verbose:
                print(f'Registered {app_file.typer_app.name} with id {id(app_file.typer_app.obj)} to {id(parent_app)} from {app_file.module} in {sub_package_name}')

    @staticmethod
    def get_typer_app_from_file(full_app_name: str) -> AppFileModule:
        return AppFileModule.from_full_app_file_name(full_app_name)



