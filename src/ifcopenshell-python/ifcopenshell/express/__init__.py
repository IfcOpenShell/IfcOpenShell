import os
import sys
import subprocess

d = os.path.abspath(os.path.dirname(__file__))
sys.path.append(d)

exp_parser_fn = os.path.join(d, "express_parser.py")

if not os.path.exists(exp_parser_fn):
    with open(exp_parser_fn, "w") as f:
        subprocess.call([sys.executable, "bootstrap.py"], cwd=d, stdout=f)

import express_parser
import schema_class
import ifcopenshell.ifcopenshell_wrapper


def parse(fn):
    mapping = express_parser.parse(fn)
    return schema_class.SchemaClass(mapping, schema_class.LateBoundSchemaInstantiator).code
