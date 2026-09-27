#!/usr/bin/env python3
"""
QUantumSrc bootstrap

Prepares a QUantumSrc checkout for development and optionally builds it.

Usage:
    python3 bootstrap.py
    python3 bootstrap.py --build
    python3 bootstrap.py --build --module server
    python3 bootstrap.py --build --module editor
    python3 bootstrap.py --clean
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_NAME = "QUantumSrc"

REQUIRED_DIRS = (
    "games",
    "mods",
    "out",
)


def run(command: list[str], cwd: Path) -> int:
    print("$", " ".join(command))
    try:
        result = subprocess.run(command, cwd=cwd)
        return result.returncode
    except FileNotFoundError:
        print(f"error: command not found: {command[0]}")
        return 127


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def check_tools() -> bool:
    print(f"Checking {PROJECT_NAME} build tools...")

    make = command_exists("make")
    compiler = command_exists("cc") or command_exists("gcc") or command_exists("clang")

    print(f"  make:    {'OK' if make else 'MISSING'}")
    print(f"  compiler:{' OK' if compiler else ' MISSING'}")

    if not make:
        print("Install GNU Make before building.")

    if not compiler:
        print("Install GCC or Clang before building.")

    return make and compiler


def find_project_root() -> Path:
    # bootstrap.py is expected to live in the repository root.
    return Path(__file__).resolve().parent


def prepare_tree(root: Path) -> None:
    print(f"Preparing {PROJECT_NAME}...")

    for relative in REQUIRED_DIRS:
        directory = root / relative
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  created: {relative}/")

    config = root / "internal" / "engine" / "config.cfg"
    if config.parent.exists() and not config.exists():
        config.write_text(
            "# QUantumSrc runtime configuration\n"
            "defaultgame=test\n"
            "mods=\n",
            encoding="utf-8",
        )
        print(f"  created: {config.relative_to(root)}")

    games = root / "games"
    test_game = games / "test"

    # Do not overwrite an existing game.
    test_game.mkdir(parents=True, exist_ok=True)
    print(f"  ready: games/test/")


def build(root: Path, module: str, jobs: int | None) -> int:
    makefile = root / "Makefile"
    if not makefile.exists():
        print("error: Makefile not found.")
        return 1

    command = ["make"]
    if jobs:
        command.append(f"-j{jobs}")

    if module != "engine":
        command.append(f"MODULE={module}")

    return run(command, root)


def clean(root: Path) -> int:
    if not (root / "Makefile").exists():
        print("error: Makefile not found.")
        return 1

    return run(["make", "clean"], root)


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Bootstrap {PROJECT_NAME}")
    parser.add_argument(
        "--build",
        action="store_true",
        help="build the engine after preparing the tree",
    )
    parser.add_argument(

