import os
import sys


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


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <folder_path> <pyproject.toml_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    pyproject_toml_path = sys.argv[2]

    whl_files = find_whl_files(folder_path)
    update_pyproject_toml(pyproject_toml_path, whl_files)
    print("pyproject.toml has been updated with the wheel files.")
