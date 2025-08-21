"""Utilities to package the AutoML executable into installable archives.

Four different packaging strategies are provided so that the build
process can choose the most appropriate installer format.  The
``create_installer_zip`` function is used by default by the build
scripts, but the other strategies are available for comparison and
testing.
"""
from __future__ import annotations

import argparse
import os
import shutil
import tarfile
import zipfile
from pathlib import Path
from typing import Iterable


def _collect_files(exe: Path, extras: Iterable[Path]) -> list[Path]:
    """Return a flat list of files to be included in the installer.

    Parameters
    ----------
    exe:
        Path to the built executable.
    extras:
        Iterable of additional files or directories.
    """
    files: list[Path] = [exe]
    for item in extras:
        path = Path(item)
        if path.is_dir():
            files.extend(p for p in path.rglob("*") if p.is_file())
        elif path.is_file():
            files.append(path)
    return files


def create_installer_zip(exe: str | os.PathLike, output: str | os.PathLike,
                         extras: Iterable[str | os.PathLike] = ()) -> Path:
    """Create a ``.zip`` archive containing the executable and extras.

    This implementation uses :class:`zipfile.ZipFile` directly.
    """
    exe_path = Path(exe)
    files = _collect_files(exe_path, [Path(x) for x in extras])
    output_path = Path(output)
    root = Path.cwd()
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            zf.write(file, file.relative_to(root))
    return output_path


def create_installer_tar(exe: str | os.PathLike, output: str | os.PathLike,
                         extras: Iterable[str | os.PathLike] = ()) -> Path:
    """Create a ``.tar.gz`` archive containing the executable and extras.

    This implementation uses :class:`tarfile.TarFile`.
    """
    exe_path = Path(exe)
    files = _collect_files(exe_path, [Path(x) for x in extras])
    output_path = Path(output)
    root = Path.cwd()
    with tarfile.open(output_path, "w:gz") as tf:
        for file in files:
            tf.add(file, arcname=file.relative_to(root))
    return output_path


def create_installer_shutil_zip(exe: str | os.PathLike,
                                output_dir: str | os.PathLike,
                                extras: Iterable[str | os.PathLike] = ()) -> Path:
    """Create a ``.zip`` archive using :func:`shutil.make_archive`."""
    exe_path = Path(exe)
    staging = exe_path.parent / "_installer_tmp"
    staging.mkdir(exist_ok=True)
    try:
        for file in _collect_files(exe_path, [Path(x) for x in extras]):
            dest = staging / file.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, dest)
        archive = shutil.make_archive(str(Path(output_dir) / "AutoML_installer"),
                                      "zip", staging)
    finally:
        shutil.rmtree(staging)
    return Path(archive)


def create_installer_shutil_targz(exe: str | os.PathLike,
                                  output_dir: str | os.PathLike,
                                  extras: Iterable[str | os.PathLike] = ()) -> Path:
    """Create a ``.tar.gz`` archive using :func:`shutil.make_archive`."""
    exe_path = Path(exe)
    staging = exe_path.parent / "_installer_tmp"
    staging.mkdir(exist_ok=True)
    try:
        for file in _collect_files(exe_path, [Path(x) for x in extras]):
            dest = staging / file.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, dest)
        archive = shutil.make_archive(str(Path(output_dir) / "AutoML_installer"),
                                      "gztar", staging)
    finally:
        shutil.rmtree(staging)
    return Path(archive)


def main() -> None:
    parser = argparse.ArgumentParser(description="Package AutoML executable")
    parser.add_argument("--exe", default="bin/AutoML.exe",
                        help="Path to the built AutoML executable")
    parser.add_argument("--output", default="bin/AutoML_installer.zip",
                        help="Output path for the installer archive")
    parser.add_argument("--method", choices=["zip", "tar", "szip", "star"],
                        default="zip", help="Packaging method")
    args = parser.parse_args()

    extras = ["README.md", "LICENSE"]
    method_map = {
        "zip": create_installer_zip,
        "tar": create_installer_tar,
        "szip": lambda exe, out, extras: create_installer_shutil_zip(exe, Path(out).parent, extras),
        "star": lambda exe, out, extras: create_installer_shutil_targz(exe, Path(out).parent, extras),
    }
    path = method_map[args.method](args.exe, args.output, extras)
    print(f"Installer created at {path}")


if __name__ == "__main__":
    main()
