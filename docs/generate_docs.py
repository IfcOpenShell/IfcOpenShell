# This program requires doxygen, sphinx, breathe and exhale.

import os
import os.path
import subprocess

from sys import platform


def copy_content(content, container):
	with open(content) as f:
		with open(container, "w") as f1:
			for line in f:
				f1.write(line)


conf_path = "./conf.py"
index_path = "./index.rst"


if not os.path.isdir("./output/doxygen/xml"):
	os.makedirs("output/doxygen/xml")

if os.path.isfile(conf_path) and not os.path.isfile(index_path):
	os.remove(conf_path) 
if os.path.isfile(index_path) and not os.path.isfile(conf_path):
	os.remove(index_path) 

if not (os.path.isfile(conf_path) and os.path.isfile(index_path)):
	subprocess.run(["sphinx-quickstart", "-q", "-p", "IfcOpenShell", "-a", "Johan Luttun"])

conf_copy = ["./conf_to_copy.py", "./conf.py"]
index_copy = ["./index_to_copy.rst", "./index.rst"]

copy_content(conf_copy[0], conf_copy[1])
copy_content(index_copy[0], index_copy[1])

if platform == "linux" or platform == "linux2":
	subprocess.run(["make", "html"])
	if not os.path.isdir("/output/_build"):
		subprocess.run(["cd","../src/ifcblenderexport/docs"])
		subprocess.run(["make", "html"])
		subprocess.run(["cd", "../../../docs"])
		
	subprocess.run(["sudo", "mv" "../src/ifcblenderexport/docs/_build", "./output"])
	
		
elif platform == "win32" or platform == "win64":
	subprocess.run(["make.bat", "html"])



