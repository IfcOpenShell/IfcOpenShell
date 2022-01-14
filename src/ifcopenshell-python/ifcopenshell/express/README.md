# IfcOpenShell express schema parser and code generator

This folder contains Python code to generate C++ type information based on an
Express schema. In particular is has only been tested using recent version of
the IFC schema and will most likely fail on any other Express schema.

The code can be invoked in the following way and results in several code outputs
named according to the schema name in the Express file. A python 3 interpreter
with the `pyparsing` (`pip install pyparsing`) library is required.

## Command line usage for code generation

~~~
# python3 bootstrap.py express.bnf > express_parser.py
python3 express_parser.py IFC2X3_TC1.exp header implementation schema_class definitions
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
