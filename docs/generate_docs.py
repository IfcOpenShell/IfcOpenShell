# This program requires doxygen, sphinx, breathe and exhale.

import os
import shutil
import subprocess

from sys import platform

conf_path = "./conf.py"
index_path = "./index.rst"

if not os.path.isdir("./output/doxygen/xml"):
	os.makedirs("output/doxygen/xml")

subprocess.check_call(["sphinx-build", "-b", "html", ".", "output"])

if platform == "linux" or platform == "linux2":
	if os.path.isdir("output/python"):
		shutil.rmtree("output/python")
	
	if not os.path.exists(os.path.join("../src/ifcblenderexport/docs", "contents.rst")):
		subprocess.check_call(["ln", "index.rst", "contents.rst"], cwd="../src/ifcblenderexport/docs")
	subprocess.check_call(["make", "html"], cwd="../src/ifcblenderexport/docs")
	shutil.move("../src/ifcblenderexport/docs/_build", "./output")
	os.rename("./output/_build", "./output/python")
		
elif platform == "win32" or platform == "win64":
	subprocess.check_call(["make.bat", "html"])
