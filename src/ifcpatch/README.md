# ifcpatch

`ifcpatch` is a little CLI utility and library that lets you run a predetermined
modification on an IFC file, known as a patch recipe. This is great for
distributing little scripts that need to modify an IFC to users who don't know
how to code or aren't interested in knowing the details.

## Installation

`ifcpatch` is a simple Python module. No compilation or packaging is necessary.
Just download the `ifcpatch` directory and add it to your Python site packages.
Then, you can run it as a CLI like:

```
$ python -m ifcpatch
```

If you want something more Unix-like ...

```
$ alias ifcpatch='python -m ifcpatch'
```

## Usage

Usage is like any other CLI app.

```
$ ifcpatch -h

usage: __main__.py [-h] -i INPUT [-o OUTPUT] -r RECIPE [-l LOG]
                   [-a ARGUMENTS [ARGUMENTS ...]]

Patches IFC files to fix badly formatted data

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        The IFC file to patch
  -o OUTPUT, --output OUTPUT
                        The output file to save the patched IFC
  -r RECIPE, --recipe RECIPE
                        Name of the recipe to use when patching
  -l LOG, --log LOG     Specify a log file
  -a ARGUMENTS [ARGUMENTS ...], --arguments ARGUMENTS [ARGUMENTS ...]
                        Specify custom arguments to the patch recipe
```

Exactly how it is run depends on the recipe. A recipe may require zero or more
arguments which are specific to the recipe. Here's an example which runs the
`ExtractElements` recipe, which, as the same suggests, extracts out elements.
This recipe expects one argument, which uses the [IFC Query
syntax](https://wiki.osarch.org/index.php?title=IfcOpenShell_code_examples#IFC_Query_Syntax).
In this example, we'll extract out all `IfcWall` elements.

```
$ ifcpatch -i input.ifc -o output.ifc -r ExtractElements -a ".IfcWall"
```

You can also use it as a library.

```
import ifcpatch
ifcpatch.execute({
    "input": "input.ifc",
    "output": "output.ifc",
    "recipe": "ExtractElements",
    "log": "ifcpatch.log",
    "arguments": [".IfcWall"],
})
```
