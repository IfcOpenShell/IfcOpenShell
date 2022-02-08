# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

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
