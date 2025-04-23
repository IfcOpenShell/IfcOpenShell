# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Nathan Hild <nathan.hild@gmail.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import sys
import subprocess
from pathlib import Path

print("Here are the detected system paths:")
print(sys.path)

py_exec = str(sys.executable)
base_python_path = str(Path(sys.executable).parent.parent)  # path without bin/python.exe

print("Detected executable:", py_exec)

subprocess.call([py_exec, "-m", "ensurepip", "--user"])
subprocess.call([py_exec, "-m", "pip", "install", "--upgrade", "pip"])

sys_paths = [p for p in sys.path if "site-packages" in p and p.startswith(base_python_path)]
if sys_paths:
    print("Detected installation directory:", sys_paths[-1])
    subprocess.call([py_exec, "-m", "pip", "install", f"--target={sys_paths[-1]}", "--upgrade", "pytest"])
    subprocess.call([py_exec, "-m", "pip", "install", f"--target={sys_paths[-1]}", "--upgrade", "pytest-bdd"])
    subprocess.call([py_exec, "-m", "pip", "install", f"--target={sys_paths[-1]}", "--upgrade", "pytest-blender"])
    subprocess.call([py_exec, "-m", "pip", "install", f"--target={sys_paths[-1]}", "--upgrade", "pygments"])
else:
    print("Could not detect installation directory. Good luck.")
    subprocess.call([py_exec, "-m", "pip", "install", "--upgrade", "pytest"])
    subprocess.call([py_exec, "-m", "pip", "install", "--upgrade", "pytest-bdd"])
    subprocess.call([py_exec, "-m", "pip", "install", "--upgrade", "pytest-blender"])
    subprocess.call([py_exec, "-m", "pip", "install", "--upgrade", "pygments"])

try:
    import pytest
    import pytest_bdd
    import pytest_blender
    import pygments

    print("Test dependency installation was successful!")
except Exception as e:
    print("Installation failed :(")
    print(e)
