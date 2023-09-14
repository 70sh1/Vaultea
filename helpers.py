import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class File:
    path: Path
    size: int


def resource_path(relative_path: str) -> Path:
    """PyInstaller filepaths fix. Works for dev env too."""
    try:
        base_path = Path(sys._MEIPASS)  # type: ignore
    except Exception:
        base_path = Path(".").absolute()

    return base_path / relative_path


def path_size(path: Path) -> int:
    """Return total size of a file or directory in bytes.
    Slightly modified version from https://peps.python.org/pep-0471/#examples"""
    total_size = 0
    try:
        if path.is_file():
            return path.stat().st_size
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                total_size += path_size(Path(entry.path))
            else:
                total_size += entry.stat(follow_symlinks=False).st_size
    except PermissionError:
        pass

    return total_size


def human_readable_size(num: int) -> str:
    kib = 1024
    mib = 1024**2
    gib = 1024**3

    if num >= gib:
        return f"({round(num/gib,2)} GiB)"
    if num >= mib:
        return f"({round(num/mib,2)} MiB)"
    if num >= kib:
        return f"({round(num/kib,2)} KiB)"

    return f"({num} bytes)"
