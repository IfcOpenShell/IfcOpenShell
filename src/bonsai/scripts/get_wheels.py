# /// script
# ///
import argparse
import os
from typing import NamedTuple


def find_whl_files(directory: str) -> list[str]:
    whl_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".whl"):
                whl_files.append(os.path.relpath(os.path.join(root, file), directory))
    whl_files.sort()
    return whl_files


def update_pyproject_toml(pyproject_path: str, whl_files: list[str]) -> None:
    with open(pyproject_path, "a") as f:
        f.write("\nwheels = [\n")
        for whl in whl_files:
            f.write(f'    "./wheels/{whl}",\n')
        f.write("]\n")


class Args(NamedTuple):
    folder_path: str
    pyproject_toml_path: str


def parse_args() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_path", help="Directory to search for .whl files.")
    parser.add_argument("pyproject_toml_path", help="TOML file to append the `wheels` list to.")
    namespace = parser.parse_args()
    return Args(folder_path=namespace.folder_path, pyproject_toml_path=namespace.pyproject_toml_path)


ARGS = parse_args()

if __name__ == "__main__":
    whl_files = find_whl_files(ARGS.folder_path)
    update_pyproject_toml(ARGS.pyproject_toml_path, whl_files)
    print("pyproject.toml has been updated with the wheel files.")
