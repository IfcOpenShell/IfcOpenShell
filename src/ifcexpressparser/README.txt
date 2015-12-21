This folder contains Python code to generate C++ type information based on an
Express schema. In particular is has only been tested using recent version of
the IFC schema and will most likely fail on any other Express schema.

The code can be invoked in the following way and results in two header files
and a single implementation file named according to the schema name in the 
Express file. A python 3 interpreter with the pyparsing [1] library is required.

$ python bootstrap.py express.bnf > express_parser.py && python express_parser.py IFC2X3_TC1.exp

[1] http://pyparsing.wikispaces.com/Download+and+Installation
