###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                          #
#                                                                             #
# IfcOpenShell is free software: you can redistribute it and/or modify        #
# it under the terms of the Lesser GNU General Public License as published by #
# the Free Software Foundation, either version 3.0 of the License, or         #
# (at your option) any later version.                                         #
#                                                                             #
# IfcOpenShell is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# Lesser GNU General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the Lesser GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################

import nodes
import platform
import collections

if tuple(map(int, platform.python_version_tuple())) < (2, 7):
    import ordereddict

    collections.OrderedDict = ordereddict.OrderedDict

# According to ISO 10303-11 7.1.2: Letters: "... The case of
# letters is significant only within explicit string literals."
class OrderedCaseInsensitiveDict_KeyObject(str):
    def __eq__(self, other):
        return self.lower() == other.lower()

    def __hash__(self):
        return hash(self.lower())


class OrderedCaseInsensitiveDict(collections.OrderedDict):
    def __init__(self, *args, **kwargs):
        collections.OrderedDict.__init__(self)
        for key, value in collections.OrderedDict(*args, **kwargs).items():
            self[OrderedCaseInsensitiveDict_KeyObject(key)] = value

    def __setitem__(self, key, value):
        return collections.OrderedDict.__setitem__(self, OrderedCaseInsensitiveDict_KeyObject(key), value)

    def __getitem__(self, key):
        return collections.OrderedDict.__getitem__(self, OrderedCaseInsensitiveDict_KeyObject(key))

    def get(self, key, *args, **kwargs):
        return collections.OrderedDict.get(self, OrderedCaseInsensitiveDict_KeyObject(key), *args, **kwargs)

    def __contains__(self, key):
        return collections.OrderedDict.__contains__(self, OrderedCaseInsensitiveDict_KeyObject(key))

    def __delitem__(self, key):
        return collections.OrderedDict.__delitem__(self, OrderedCaseInsensitiveDict_KeyObject(key))


class Schema:
    def is_enumeration(self, v):
        return str(v) in self.enumerations

    def is_select(self, v):
        return str(v) in self.selects

    def is_simpletype(self, v):
        return str(v) in self.simpletypes

    def is_type(self, v):
        return str(v) in self.types

    def is_entity(self, v):
        return str(v) in self.entities

    def __len__(self):
        return len(self.types) + len(self.entities)

    def __iter__(self):
        return iter(self.keys)

    def __getitem__(self, key):
        return self.types_entities[key]

    def __init__(self, parsetree):
        self.name = parsetree.syntax[0][0].simple_id

        sort = lambda d: OrderedCaseInsensitiveDict(sorted(d))

        declarations = [
            d.any()[0]
            for d in parsetree.syntax[0][0].schema_body[0]
            if d.rule == "declaration" and d.any()[0].rule != "function_decl"
        ]

        self.types = sort([(t.name, t) for t in declarations if isinstance(t, nodes.TypeDeclaration)])
        self.entities = sort([(t.name, t) for t in declarations if isinstance(t, nodes.EntityDeclaration)])

        self.keys = list(self.types.keys()) + list(self.entities.keys())
        self.types_entities = {k: v for d in (self.types, self.entities) for k, v in d.items()}

        of_type = lambda *types: sort(
            [(a, b.type) for a, b in self.types.items() if any(isinstance(b.type, ty) for ty in types)]
        )

        self.enumerations = of_type(nodes.EnumerationType)
        self.selects = of_type(nodes.SelectType)
        self.simpletypes = of_type(
            str, nodes.AggregationType, nodes.BinaryType, nodes.StringType, nodes.SimpleType, nodes.NamedType
        )

        assert len(self.enumerations) + len(self.selects) + len(self.simpletypes) == len(self.types)
