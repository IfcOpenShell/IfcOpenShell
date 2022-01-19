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


import operator

import nodes
import codegen

from collections import defaultdict


class Definitions(codegen.Base):
    def __init__(self, mapping):

        schema_name = mapping.schema.name
        self.schema_name = schema_name_title = schema_name.capitalize()

        statements = [""]

        def write_entity(schema_name, name, type):

            attribute_names = list(map(lambda t: (t.name, t.optional), type.attributes))
            for attr, is_optional in attribute_names:
                statements.append("#define SCHEMA_%(name)s_HAS_%(attr)s" % locals())
                if is_optional:
                    statements.append("#define SCHEMA_%(name)s_%(attr)s_IS_OPTIONAL" % locals())
            inverse_attribute_names = list(map(operator.attrgetter("name"), type.inverse))
            for attr in inverse_attribute_names:
                statements.append("#define SCHEMA_%(name)s_HAS_%(attr)s" % locals())

        def write(name):
            statements.append("#define SCHEMA_HAS_%(name)s" % locals())
            fn = None
            if mapping.schema.is_entity(name):
                fn = write_entity

            if fn is not None:
                decl = mapping.schema[name]
                if isinstance(decl, nodes.TypeDeclaration):
                    decl = decl.type.type
                fn(schema_name, name, decl) is not False

        for name in mapping.schema:
            write(name)

        self.str = "\n".join(statements) + "\n"

        self.file_name = "%s-definitions.h" % self.schema_name

    def __repr__(self):
        return self.str


Generator = Definitions
