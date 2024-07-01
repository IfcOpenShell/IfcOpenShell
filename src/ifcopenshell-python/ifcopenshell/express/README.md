# IfcOpenShell express schema parser and code generator

This folder contains Python code to generate C++ type information based on an
Express schema. In particular is has only been tested using recent version of
the IFC schema and will most likely fail on any other Express schema.

The code can be invoked in the following way and results in several code outputs
named according to the schema name in the Express file. A python 3 interpreter
with the `pyparsing` (`pip install pyparsing`) library is required.

note: 
**Keep in mind that Express is not very suitable for this kind of usage. In the end, (as far as I can tell) no tool is able to read your model, because it doesn't understand the schema as it has no notion of the core part vs the addition.**

## Command line usage for code generation

The usage for C++ project.
~~~
# bootstrap.py express.bnf in ifcopenshell-python.ifcopenshell.express.
>>> python3 bootstrap.py express.bnf > express_parser.py
>>> python3 express_parser.py IFC2X3_TC1.exp header implementation schema_class definitions
~~~

The usage for python project.
~~~
# code rule generation
# generating 'ifcopenshell.express.rules.IFC2X3_TC1' in ifcopenshell-python.ifcopenshell.express.rules.
# rule_compiler in ifcopenshell-python.ifcopenshell.express.
>>> python -m rule_compiler IFC2X3_TC1.exp
~~~

## Programmatic usage

~~~py
import ifcopenshell
import ifcopenshell.express
schema = ifcopenshell.express.parse('IFC.exp')
ifcopenshell.register_schema(schema)
f = ifcopenshell.file(schema=schema.schema.name())
f.createIfcProject(ifcopenshell.guid.new())
~~~
