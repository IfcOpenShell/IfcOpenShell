# This program requires doxygen, sphinx, breathe and exhale.

import os
import sys
import shutil
import subprocess
import multiprocessing

# some extra check to see if we can find sphinx in pypy bin dir
sphinx_build = os.path.join(os.path.dirname(sys.executable), 'sphinx-build')
if not os.path.exists(sphinx_build):
	sphinx_build = "sphinx-build"
else:
	os.environ['PATH'] += os.pathsep + os.path.dirname(sys.executable)

# not used, -j caused issues in my sphinx install
j = str(multiprocessing.cpu_count())

if not os.path.isdir("./output/doxygen/xml"):
	os.makedirs("output/doxygen/xml")

subprocess.check_call([sphinx_build, "-b", "html", ".", "output"])

if sys.platform == "linux" or sys.platform == "linux2":
	if os.path.isdir("output/python"):
		shutil.rmtree("output/python")
	
	if not os.path.exists(os.path.join("../src/ifcblenderexport/docs", "contents.rst")):
		subprocess.check_call(["ln", "index.rst", "contents.rst"], cwd="../src/ifcblenderexport/docs")
	
	subprocess.check_call(["sed", "-i", "s/html_theme/# html_theme/g", "conf.py"], cwd="../src/ifcblenderexport/docs"))
	subprocess.check_call(["make", "html"], cwd="../src/ifcblenderexport/docs")
	subprocess.check_call(["git", "checkout", "conf.py"], cwd="../src/ifcblenderexport/docs"))
	
	shutil.move("../src/ifcblenderexport/docs/_build", "./output")
	os.rename("./output/_build", "./output/python")
		
elif sys.platform == "win32" or sys.platform == "win64":
	subprocess.check_call(["make.bat", "html"])
