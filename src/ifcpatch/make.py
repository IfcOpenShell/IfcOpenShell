#!/usr/bin/env python3
import os
import subprocess

cmd = f'pyinstaller ./bootstrap.py --name ifcpatch --onefile --clean --add-data "ifcpatch{os.pathsep}ifcpatch"'
subprocess.check_output(cmd, shell=True)
