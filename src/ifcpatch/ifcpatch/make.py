#!/usr/bin/env python3
import os
import subprocess

# add hidden imports in recipes here
HIDDEN_IMPORTS = [
    "ifcopenshell.util.selector",
    "ifcopenshell.util.element",
    "ifcopenshell.util.schema",
    "toposort",
]


def main():
    hiddenimport_args = " ".join('--hiddenimport "{}"'.format(imp) for imp in HIDDEN_IMPORTS)
    cmd = 'pyinstaller ./__init__.py --onefile --clean --add-data ".{}ifcpatch" {}'.format(
        os.pathsep, hiddenimport_args
    )
    subprocess.check_output(cmd, shell=True)


if __name__ == "__main__":
    main()
