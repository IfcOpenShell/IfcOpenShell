import re
import argparse
from pathlib import Path

def update_version(file_path: str, version: str) -> None:
    """Update the version string in the given __init__.py file."""
    file_path = Path(file_path)

    # Read the file and replace the version
    file_contents = file_path.read_text(encoding="utf-8")
    new_contents = re.sub(r'version = "0\.0\.0"', f'version = "{version}"', file_contents)

    # Write the updated contents back to the file
    file_path.write_text(new_contents, encoding="utf-8")

    print(f"Updated version in {file_path} to {version}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update the version string in a Python file.")
    parser.add_argument(
        "version",
        type=str,
        help="The version string to replace '0.0.0' with (e.g., '1.2.3')."
    )
    parser.add_argument(
        "file",
        type=str,
        help="The path to the __init__.py file where the version will be updated."
    )

    args = parser.parse_args()
    update_version(args.file, args.version)
