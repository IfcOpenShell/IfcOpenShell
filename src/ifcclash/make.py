#!/usr/bin/env python3
import os
import subprocess


cmd = "pyinstaller ./bootstrap.py --name ifcclash --onefile --clean"
subprocess.check_output(cmd, shell=True)
