import importlib.util
import inspect
import logging
import sys
from pathlib import Path
from types import ModuleType
from typing import List

from libs.commands import commands

log = logging.getLogger(__name__)

def folder_import(folder: str, show_traceback: bool = False) -> List[ModuleType]:
    """
    Import every .py file directly inside `folder` (skip __init__.py).
    Imported modules are placed in sys.modules as "<folder_name>.<module_stem>".
    Returns the list of imported module objects.
    """
    folder_path = Path(folder).resolve()
    if not folder_path.is_dir():
        raise NotADirectoryError(folder_path)

    package_prefix = folder_path.name
    imported_modules: List[ModuleType] = []
    imported_modules_names: List[str] = []

    for candidate in folder_path.iterdir():
        if candidate.suffix != ".py" or candidate.name == "__init__.py":
            continue

        module_name = f"{package_prefix}.{candidate.stem}"
        spec = importlib.util.spec_from_file_location(module_name, str(candidate))
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot create import spec for {candidate}")

        module = importlib.util.module_from_spec(spec)
        # register before execution so other modules can import it by name
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception as err:
            log.warning(f"Was not able to import: {module_name}")
            log.warning(err, exc_info=show_traceback)
            continue

        imported_modules_names.append(candidate.stem)
        imported_modules.append(module)

    log.info(f"Imported the following modules: {", ".join(imported_modules_names)}")
    return imported_modules


def calling_module_name():
    current_frame = inspect.currentframe()
    walker = current_frame
    try:
        while walker:
            walker = walker.f_back
            if not walker:
                break
            candidate = walker.f_globals.get("__name__", "")
            if candidate and candidate not in (__name__, "lib.commands", "logging"):
                return candidate
    finally:
        try:
            del current_frame
        except Exception:
            pass
    return "__main__"


class LoggerProxy:
    def __getattr__(self, attribute_name):
        return lambda *positional_args, **keyword_args: getattr(
            logging.getLogger(calling_module_name()), attribute_name
        )(*positional_args, **keyword_args)


log = LoggerProxy()
register = commands.register
