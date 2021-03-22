# BIMTester

BIMTester lets you specify a set of exchange requirements, and automatically check whether or not BIM data, typically an
IFC file, complies with the requirements. You can run it automatically from a server, integrate it to your own
application, or use a GUI. It can generate reports in various formats including:

 * HTML
 * JSON
 * XUnit
 * BCF (TODO)
 * Zoom Smart View (Someone needs to check if this works)

Your exchange requirements are written in plain language which you can use to communicate to project teams and include
in contracts. Multiple languages are supported. A series of exchange requirement templates are provided to get started,
but you can, and are encouraged to, write your own tailored to your project. An example of a requirement looks like
this:

```
Feature: Project setup

In order to view the BIM data
As any interested stakeholder
We need an IFC file

Scenario: Receiving a file
 * IFC data must use the "IFC4" schema
```

Languages supported include (in alphabetical order):

 * Dutch
 * English
 * French
 * German
 * Italian

If you are not a developer, we highly recommend simply installing an integrated version of BIMTester.

 * If you use Blender, install the [BlenderBIM Add-on](https://blenderbim.org)
 * If you use FreeCAD, install the [FreeCAD BIMTester Workbench](https://github.com/bimtester/bimtesterfc)

If you are a developer, read on!

## Installation

The following packages are required for BIMTester to function:

 * behave
 * pystache
 * ifcopenshell
 * PySide2 (optional: needed for GUI)

The repository does not contain translation files. You can generate them as shown.

```
cd IfcOpenShell/src/ifcbimtester/bimtester/locale
pybabel compile -d .
```

## CLI Usage

BIMTester has a command line application. Check it out:

```
$ python cli.py -h
usage: cli.py [-h] [-a ACTION] [--advanced-arguments ADVANCED_ARGUMENTS] [-c]
              -f FEATURE -i IFC [-p PATH] [-r REPORT] [--lang LANG]

Runs unit tests for BIM data

optional arguments:
  -h, --help            show this help message and exit
  -a ACTION, --action ACTION
                        Action to perform, from run/purge
  --advanced-arguments ADVANCED_ARGUMENTS
                        Specify arguments to Behave
  -c, --console         Show results in the console
  -f FEATURE, --feature FEATURE
                        Specify a feature file to test
  -i IFC, --ifc IFC     Specify a ifc file
  -p PATH, --path PATH  Define a path for use in tests
  -r REPORT, --report REPORT
                        Specify an output file for a HTML report
  --lang LANG           Specify a language
```

You can turn it into a regular command by symlinking it to your bin folder.

```
$ ln -s /path/to/IfcOpenShell/src/ifcbimtester/cli.py /usr/local/bin/bimtester
$ bimtester -h
```

To run a test, we need an IFC to check and a feature file filled with requirements. The feature file is plaintext. Feel
free to copy the minimal example above.

```
# To see output in the console
$ bimtester -i test.ifc -f test.feature -c
# Or, if you want to generate a HTML report
$ bimtester -i test.ifc -f test.feature -r report.html
```

```
python ./gui.py
```

## Create a binary out of the Python package

TODO: Check if this works

Unix:

```
$ pyinstaller --onefile --clean --icon=icon.ico --add-data "features:features" bimtester.py
```

Windows:

```
$ pyinstaller --onefile --clean --icon=icon.ico --add-data "features;features" bimtester.py
```
